"""
app/ml/training/trainer.py
 
Trains two XGBoost classifiers:
  1. winner_model   — predicts race winner (binary: is_winner)
  2. podium_model   — predicts podium finish (binary: is_podium)
 
Training rules:
  - Time-based split ONLY — never random split (leaks future data)
  - Reads from features_by_race where finish_position IS NOT NULL
  - Saves artifacts to models/ directory
  - Registers run in MLflow
  - Never auto-promotes to production — evaluator decides that separately
 
Artifact files written:
  models/xgb_winner.json
  models/xgb_podium.json
  models/metadata.json       — feature columns, label encoders, version info
"""
 
import json
import os
from datetime import datetime, timezone
from pathlib import Path
 
import mlflow
import numpy as np
import pandas as pd
from sklearn.preprocessing import LabelEncoder
from xgboost import XGBClassifier
 
from app.core.logging import get_logger
from app.db.repositories.feature_repo import FeatureRepository, CURRENT_FEATURE_VERSION
 
logger = get_logger(__name__)
 
MODELS_DIR = Path(os.environ.get("MODELS_DIR", "models"))
MODELS_DIR.mkdir(exist_ok=True)
 
# Feature columns the model trains on
# Changing this list = bump CURRENT_FEATURE_VERSION in feature_repo.py
FEATURE_COLUMNS = [
    "avg_finish_last_5",
    "avg_quali_last_5",
    "podium_rate",
    "dnf_rate",
    "teammate_delta",
    "constructor_form",
    "reliability_score",
    "qualifying_position",
]

# Categorical columns that need label encoding
CATEGORICAL_COLUMNS = ["driver_code", "team_id", "circuit_id"]
 
# Validation split — season-aware
# Train: all seasons except the current season
# Validate: current season only
 
 
def retrain_from_supabase(
    feature_version: str = CURRENT_FEATURE_VERSION,
    from_year: int = 2018,
    mlflow_experiment: str = "f1_prediction",
) -> dict:
    """
    Full training pipeline. Called by the Prefect retrain flow.
 
    Returns metrics dict:
      {
        "winner_top3_accuracy": float,
        "winner_exact_accuracy": float,
        "podium_accuracy": float,
        "training_rows": int,
        "validation_races": int,
        "run_id": str,
      }
    """
    logger.info(f"Retraining started feature_version={feature_version} from_year={from_year}")

    # ---------------Step 1: Load training dataset----------------------------------------------------
    repo = FeatureRepository()
    df = repo.get_training_dataset(feature_version=feature_version, from_year=from_year)

    data_cutoff_timestamp = "unknown"
    if "computed_at" in df.columns:
        max_computed_at = pd.to_datetime(df["computed_at"], utc=True, errors="coerce").max()
        if pd.notna(max_computed_at):
            data_cutoff_timestamp = max_computed_at.isoformat()

    training_dataset_hash = str(pd.util.hash_pandas_object(df, index=True).sum())
 
    if df.empty:
        raise ValueError("Training dataset is empty — no features with known results")
 
    if len(df) < 100:
        raise ValueError(
            f"Training dataset too small: {len(df)} rows. "
            "Need at least 100. Run backfill first."
        )
 
    logger.info(f"Loaded {len(df)} training rows")

    # --------------Step 2: Encode categoricals + fill nulls-------------------------------------------------------
    df, encoders = _encode_and_clean(df)
 
    # --------Step 3: Time-based train/validation split--------------------------------------------
    df = df.sort_values(["year", "round"]).reset_index(drop=True)

    current_year = int(df["year"].max())
    val_mask = df["year"] == current_year
 
    train_df = df[~val_mask].copy()
    val_df = df[val_mask].copy()

    validation_races = int(val_df[["year", "round"]].drop_duplicates().shape[0])
 
    logger.info(
        f"Split: {len(train_df)} train rows, {len(val_df)} val rows "
        f"(validation season={current_year}, {validation_races} races)"
    )
 
    all_feature_cols = FEATURE_COLUMNS + [f"{c}_encoded" for c in CATEGORICAL_COLUMNS]
    available_cols = [c for c in all_feature_cols if c in train_df.columns]

    raw_categoricals_in_features = [c for c in CATEGORICAL_COLUMNS if c in available_cols]
    if raw_categoricals_in_features:
        raise ValueError(
            "Raw categorical columns must not be used as model features; "
            f"use *_encoded instead. Found: {raw_categoricals_in_features}"
        )
 
    X_train = train_df[available_cols]
    X_val = val_df[available_cols]
    y_winner_train = train_df["is_winner"]
    y_winner_val = val_df["is_winner"]
    y_podium_train = train_df["is_podium"]
    y_podium_val = val_df["is_podium"]


    # -----------Step 4: Train models---------------------------------------
    logger.info("Training winner model...")
    winner_model = _train_xgboost(X_train, y_winner_train, label="winner")
 
    logger.info("Training podium model...")
    podium_model = _train_xgboost(X_train, y_podium_train, label="podium")
 
    # -----------Step 5: Evaluate-------------------------------------------------------
    metrics = _evaluate(
        winner_model, podium_model,
        X_val, y_winner_val, y_podium_val,
        val_df,
    )
    metrics["training_rows"] = len(train_df)
    metrics["validation_races"] = validation_races
 
    logger.info(f"Evaluation: {metrics}")


    # ------------Step 6: Save artifacts---------------------------------------------------------
    winner_model.save_model(str(MODELS_DIR / "xgb_winner.json"))
    podium_model.save_model(str(MODELS_DIR / "xgb_podium.json"))
 
    metadata = {
        "feature_version": feature_version,
        "data_cutoff_timestamp": data_cutoff_timestamp,
        "training_dataset_hash": training_dataset_hash,
        "feature_columns": available_cols,
        "categorical_columns": CATEGORICAL_COLUMNS,
        "categorical_encoding": {
            "method": "LabelEncoder",
            "encoded_columns": [f"{c}_encoded" for c in CATEGORICAL_COLUMNS],
            "note": (
                "Encoded categorical IDs are nominal (no ordinal meaning). "
                "Do not interpret higher/lower encoded values as better/worse; "
                "feature importance for *_encoded means the category identity matters, not the magnitude."
            ),
        },
        "encoder_classes": {
            col: enc.classes_.tolist()
            for col, enc in encoders.items()
        },
        "training_window": {"from_year": from_year},
        "trained_at": datetime.now(timezone.utc).isoformat(),
        "metrics": metrics,
    }
 
    with open(MODELS_DIR / "metadata.json", "w") as f:
        json.dump(metadata, f, indent=2)
 
    logger.info(f"Artifacts saved to {MODELS_DIR}")


    # ---------Step 7: Register in MLflow-----------------------------------------------------
    run_id = _register_mlflow_run(
        mlflow_experiment, metrics, metadata,
        winner_model, podium_model,
        X_train=X_train,
        available_cols=available_cols,
    )
    metrics["run_id"] = run_id
 
    logger.info(f"Retraining complete run_id={run_id}")
    return metrics


    # -------------Internal helpers---------------------------------------
 
def _encode_and_clean(df: pd.DataFrame) -> tuple[pd.DataFrame, dict]:
    """
    Label-encode categorical columns and fill nulls with column medians.
    Returns the encoded DataFrame and the fitted encoders dict.
    """
    encoders = {}
    df = df.copy()
 
    for col in CATEGORICAL_COLUMNS:
        if col in df.columns:
            enc = LabelEncoder()
            df[f"{col}_encoded"] = enc.fit_transform(df[col].fillna("unknown"))
            encoders[col] = enc
 
    # Fill numeric nulls with column median
    for col in FEATURE_COLUMNS:
        if col in df.columns:
            median = df[col].median()
            df[col] = df[col].fillna(median if pd.notna(median) else 0.0)
 
    return df, encoders


def _train_xgboost(X: pd.DataFrame, y: pd.Series, label: str) -> XGBClassifier:
    """Train a single XGBoost binary classifier."""
    scale_pos_weight = float((y == 0).sum()) / max(float((y == 1).sum()), 1)
 
    model = XGBClassifier(
        n_estimators=200,
        max_depth=4,
        learning_rate=0.05,
        subsample=0.8,
        colsample_bytree=0.8,
        scale_pos_weight=scale_pos_weight,  # handle class imbalance
        use_label_encoder=False,
        eval_metric="logloss",
        random_state=42,
        verbosity=0,
    )
    model.fit(X, y)
    logger.info(f"{label} model trained on {len(X)} rows")
    return model

def _evaluate(
    winner_model: XGBClassifier,
    podium_model: XGBClassifier,
    X_val: pd.DataFrame,
    y_winner_val: pd.Series,
    y_podium_val: pd.Series,
    val_df: pd.DataFrame,
) -> dict:
    """
    Evaluate both models on the validation set.
 
    Metrics:
      winner_exact_accuracy  — fraction of races where predicted winner = actual winner
      winner_top3_accuracy   — fraction of races where actual winner is in top-3 predicted
      podium_accuracy        — fraction of podium predictions correct across all drivers
    """
    winner_probs = winner_model.predict_proba(X_val)[:, 1]
    podium_probs = podium_model.predict_proba(X_val)[:, 1]
 
    val_df = val_df.copy()
    val_df["winner_prob"] = winner_probs
    val_df["podium_prob"] = podium_probs
 
    winner_exact = 0
    winner_top3 = 0
    total_races = 0
 
    for (year, round_num), race in val_df.groupby(["year", "round"]):
        actual_winner = race[race["is_winner"] == 1]
        if actual_winner.empty:
            continue
 
        predicted_top3 = race.nlargest(3, "winner_prob")["driver_code"].tolist()
        predicted_winner = race.nlargest(1, "winner_prob")["driver_code"].iloc[0]
        actual_winner_code = actual_winner["driver_code"].iloc[0]
 
        if predicted_winner == actual_winner_code:
            winner_exact += 1
        if actual_winner_code in predicted_top3:
            winner_top3 += 1
        total_races += 1
 
    podium_preds = (podium_probs >= 0.5).astype(int)
    podium_accuracy = float((podium_preds == y_podium_val.values).mean())
 
    return {
        "winner_exact_accuracy": round(winner_exact / max(total_races, 1), 4),
        "winner_top3_accuracy": round(winner_top3 / max(total_races, 1), 4),
        "podium_accuracy": round(podium_accuracy, 4),
    }


def _log_feature_importance(model, feature_names: list, filename: str) -> None:
    """Log feature importance for a trained XGBoost model to MLflow as a CSV artifact."""
    importance_df = pd.DataFrame({
        "feature": feature_names,
        "importance": model.feature_importances_
    }).sort_values("importance", ascending=False)
    
    csv_path = MODELS_DIR / filename
    importance_df.to_csv(csv_path, index=False)
    mlflow.log_artifact(str(csv_path))
    logger.info(f"Logged feature importance to {filename}")


def _register_mlflow_run(
    experiment_name: str,
    metrics: dict,
    metadata: dict,
    winner_model,
    podium_model,
    X_train: pd.DataFrame = None,
    available_cols: list = None,
) -> str:
    """Log the training run to MLflow. Returns the run_id.
    
    Args:
        experiment_name: MLflow experiment name
        metrics: Evaluation metrics dict
        metadata: Training metadata dict
        winner_model: Trained winner XGBoost classifier
        podium_model: Trained podium XGBoost classifier
        X_train: Training feature matrix for input example
        available_cols: List of feature column names
    """
    try:
        mlflow.set_experiment(experiment_name)
        with mlflow.start_run() as run:
            mlflow.log_params({
                "feature_version": metadata["feature_version"],
                "data_cutoff_timestamp": metadata.get("data_cutoff_timestamp", "unknown"),
                "training_dataset_hash": metadata.get("training_dataset_hash", "unknown"),
                "categorical_encoding": "LabelEncoder",
                "categorical_columns": ",".join(metadata.get("categorical_columns", [])),
                "from_year": metadata["training_window"]["from_year"],
                "training_rows": metrics["training_rows"],
                "validation_races": metrics["validation_races"],
                "n_feature_columns": len(metadata["feature_columns"]),
            })
            mlflow.log_metrics({
                "winner_exact_accuracy": metrics["winner_exact_accuracy"],
                "winner_top3_accuracy": metrics["winner_top3_accuracy"],
                "podium_accuracy": metrics["podium_accuracy"],
            })
            
            # Log feature importance for both models
            if available_cols:
                _log_feature_importance(winner_model, available_cols, "winner_feature_importance.csv")
                _log_feature_importance(podium_model, available_cols, "podium_feature_importance.csv")
            
            # Log models with input examples so MLflow can infer signature
            input_example = X_train.iloc[:5] if X_train is not None else None
            mlflow.xgboost.log_model(
                winner_model,
                artifact_path="winner_model",
                input_example=input_example
            )
            mlflow.xgboost.log_model(
                podium_model,
                artifact_path="podium_model",
                input_example=input_example
            )
            return run.info.run_id
    except Exception as e:
        logger.error(f"MLflow registration failed (non-fatal): {e}")
        return "mlflow_unavailable"