"""
app/services/prediction_service.py

Orchestrates the offline inference step: reads features → runs engine → stores predictions.
Also serves as the read layer for the API (thin wrappers over prediction_repo).

The API only calls the read methods.
The Prefect flow calls run_inference_for_race().
"""

from app.core.logging import get_logger
from app.db.repositories.feature_repo import FeatureRepository
from app.db.repositories.prediction_repo import PredictionRepository
from app.ml.inference.loader import get_engine

logger = get_logger(__name__)

_feature_repo = FeatureRepository()
_prediction_repo = PredictionRepository()


def run_inference_for_race(race_key: str) -> dict:
    """
    Full offline inference pipeline for one race:
      1. Load features from features_by_race
      2. Run InferenceEngine.predict()
      3. Upsert to predictions table

    Called by Prefect after feature_engineering_flow completes.
    Returns a summary dict.
    """
    engine = get_engine()

    features_df = _feature_repo.get_features_for_race(
        race_key=race_key,
        feature_version=engine.feature_version,
    )

    if features_df.empty:
        logger.error(f"No features found for inference race_key={race_key}")
        return {"race_key": race_key, "rows_stored": 0, "status": "no_features"}

    predictions_df = engine.predict(features_df)

    # Attach model metadata
    predictions_df["model_version"] = engine.model_version
    predictions_df["feature_version"] = engine.feature_version

    rows_stored = _prediction_repo.upsert_predictions(predictions_df)

    logger.info(
        f"Inference complete race_key={race_key} "
        f"rows={rows_stored} model={engine.model_version}"
    )
    return {
        "race_key": race_key,
        "rows_stored": rows_stored,
        "model_version": engine.model_version,
        "feature_version": engine.feature_version,
        "status": "completed",
    }

# ------------------------------Read methods — called by API route handlers----------------------------------------

def get_predictions(race_key: str) -> list[dict]:
    df = _prediction_repo.get_predictions_for_race(race_key)
    return _df_to_list(df)


def get_latest_predictions() -> list[dict]:
    df = _prediction_repo.get_latest_predictions()
    return _df_to_list(df)


def list_races() -> list[str]:
    return _prediction_repo.list_race_keys()


def _df_to_list(df) -> list[dict]:
    if df.empty:
        return []
    # Convert timestamps to ISO strings for JSON serialisation
    if "generated_at" in df.columns:
        df["generated_at"] = df["generated_at"].astype(str)
    return df.to_dict(orient="records")