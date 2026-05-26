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
    "wet_weather_score",
    "teammate_delta",
    "tire_management_score",
    "constructor_form",
    "reliability_score",
    "overtaking_difficulty",
    "tire_deg_factor",
    "safety_car_probability",
    "qualifying_position",
    "qualifying_delta_to_pole",
]

# Categorical columns that need label encoding
CATEGORICAL_COLUMNS = ["driver_code", "team_id", "circuit_id"]
 
# Validation split — last N races held out for evaluation
VALIDATION_RACES = 10
 
 
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

    # ------------------------------------------------------------------
    # Step 1: Load training dataset
    # ------------------------------------------------------------------
    repo = FeatureRepository()
    df = repo.get_training_dataset(feature_version=feature_version, from_year=from_year)
 
    if df.empty:
        raise ValueError("Training dataset is empty — no features with known results")
 
    if len(df) < 100:
        raise ValueError(
            f"Training dataset too small: {len(df)} rows. "
            "Need at least 100. Run backfill first."
        )
 
    logger.info(f"Loaded {len(df)} training rows")

    # ------------------------------------------------------------------
    # Step 2: Encode categoricals + fill nulls
    # ------------------------------------------------------------------
    df, encoders = _encode_and_clean(df)
 
    # ------------------------------------------------------------------
    # Step 3: Time-based train/validation split
    # ------------------------------------------------------------------
    df = df.sort_values(["year", "round"]).reset_index(drop=True)
 
    # Get the last VALIDATION_RACES unique (year, round) combinations
    unique_races = df[["year", "round"]].drop_duplicates().tail(VALIDATION_RACES)
    val_mask = df.set_index(["year", "round"]).index.isin(
        unique_races.set_index(["year", "round"]).index
    )
 
    train_df = df[~val_mask].copy()
    val_df = df[val_mask].copy()
 
    logger.info(
        f"Split: {len(train_df)} train rows, {len(val_df)} val rows "
        f"({VALIDATION_RACES} validation races)"
    )
 
    all_feature_cols = FEATURE_COLUMNS + [f"{c}_encoded" for c in CATEGORICAL_COLUMNS]
    available_cols = [c for c in all_feature_cols if c in train_df.columns]
 
    X_train = train_df[available_cols]
    X_val = val_df[available_cols]
    y_winner_train = train_df["is_winner"]
    y_winner_val = val_df["is_winner"]
    y_podium_train = train_df["is_podium"]
    y_podium_val = val_df["is_podium"]


    # ------------------------------------------------------------------
    # Step 4: Train models
    # ------------------------------------------------------------------
    logger.info("Training winner model...")
    winner_model = _train_xgboost(X_train, y_winner_train, label="winner")
 
    logger.info("Training podium model...")
    podium_model = _train_xgboost(X_train, y_podium_train, label="podium")
 
    # ------------------------------------------------------------------
    # Step 5: Evaluate
    # ------------------------------------------------------------------
    metrics = _evaluate(
        winner_model, podium_model,
        X_val, y_winner_val, y_podium_val,
        val_df,
    )
    metrics["training_rows"] = len(train_df)
    metrics["validation_races"] = VALIDATION_RACES
 
    logger.info(f"Evaluation: {metrics}")


    # ------------------------------------------------------------------
    # Step 6: Save artifacts
    # ------------------------------------------------------------------
    winner_model.save_model(str(MODELS_DIR / "xgb_winner.json"))
    podium_model.save_model(str(MODELS_DIR / "xgb_podium.json"))
 
    metadata = {
        "feature_version": feature_version,
        "feature_columns": available_cols,
        "categorical_columns": CATEGORICAL_COLUMNS,
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


    # ------------------------------------------------------------------
    # Step 7: Register in MLflow
    # ------------------------------------------------------------------
    run_id = _register_mlflow_run(
        mlflow_experiment, metrics, metadata,
        winner_model, podium_model,
    )
    metrics["run_id"] = run_id
 
    logger.info(f"Retraining complete run_id={run_id}")
    return metrics


    # ---------------------------------------------------------------------------
# Internal helpers
# ---------------------------------------------------------------------------
 
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