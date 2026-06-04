"""
GET /api/v1/health        → API process alive
GET /api/v1/health/db     → Supabase reachable + prediction staleness
GET /api/v1/health/model  → model artifacts loaded
"""

from datetime import datetime, timezone
from fastapi import APIRouter
from fastapi.responses import JSONResponse

from app.db.session import check_connection
from app.db.repositories.prediction_repo import PredictionRepository
from app.ml.inference.loader import engine_is_loaded, get_engine
from app.core.logging import get_logger

logger = get_logger(__name__)
router = APIRouter(prefix="/health", tags=["health"])

_prediction_repo = PredictionRepository()

# Alert if no predictions exist newer than this many days during race season
STALENESS_DAYS = 10


@router.api_route("", methods=["GET", "HEAD"])
def health():
    return {
        "status": "ok",
        "timestamp": datetime.now(timezone.utc).isoformat(),
    }


@router.get("/db")
def health_db():
    db_ok = check_connection()
    status = {"db_connected": db_ok}

    # Staleness check
    try:
        most_recent = _prediction_repo.get_most_recent_generated_at()
        if most_recent is None:
            status["predictions_stale"] = True
            status["predictions_age_days"] = None
            status["detail"] = "No predictions stored yet"
        else:
            if most_recent.tzinfo is None:
                most_recent = most_recent.replace(tzinfo=timezone.utc)
            age_days = (datetime.now(timezone.utc) - most_recent).days
            stale = age_days > STALENESS_DAYS
            status["predictions_stale"] = stale
            status["predictions_age_days"] = age_days
            status["last_prediction_at"] = most_recent.isoformat()
    except Exception as e:
        logger.error(f"Staleness check failed: {e}")
        status["predictions_stale"] = None
        status["staleness_check_error"] = str(e)

    healthy = db_ok and not status.get("predictions_stale")
    code = 200 if healthy else 503
    return JSONResponse(status_code=code, content={"status": "ok" if healthy else "degraded", **status})

@router.get("/model")
def health_model():
    if not engine_is_loaded():
        return JSONResponse(
            status_code=503,
            content={"status": "not_loaded", "detail": "Model not yet loaded"},
        )
    try:
        engine = get_engine()
        return {
            "status": "ok",
            "model_version": engine.model_version,
            "feature_version": engine.feature_version,
            "feature_columns": len(engine.feature_columns),
        }
    except Exception as e:
        logger.error(f"Model health check failed: {e}")
        return JSONResponse(
            status_code=503,
            content={"status": "error", "detail": str(e)},
        )