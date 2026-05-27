"""
GET /api/v1/predictions          → latest race predictions
GET /api/v1/predictions/races    → list all race keys with stored predictions
GET /api/v1/predictions/{race_key} → predictions for a specific race
"""

from fastapi import APIRouter, HTTPException
from app.services import prediction_service
from app.core.logging import get_logger

logger = get_logger(__name__)
router = APIRouter(prefix="/predictions", tags=["predictions"])


@router.get("")
def get_latest_predictions():
    """Return predictions for the most recently processed race."""
    predictions = prediction_service.get_latest_predictions()
    if not predictions:
        raise HTTPException(status_code=404, detail="No predictions available yet")
    return {
        "race_key": predictions[0]["race_key"],
        "generated_at": predictions[0]["generated_at"],
        "model_version": predictions[0]["model_version"],
        "predictions": predictions,
    }


@router.get("/races")
def list_races():
    """Return all race keys that have stored predictions."""
    return {"races": prediction_service.list_races()}


@router.get("/{race_key}")
def get_predictions_for_race(race_key: str):
    """Return predictions for a specific race key."""
    predictions = prediction_service.get_predictions(race_key)
    if not predictions:
        raise HTTPException(
            status_code=404,
            detail=f"No predictions found for race_key={race_key}",
        )
    return {
        "race_key": race_key,
        "generated_at": predictions[0]["generated_at"],
        "model_version": predictions[0]["model_version"],
        "predictions": predictions,
    }