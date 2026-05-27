"""
Prefect tasks for offline inference.
Called by post_qualifying_flow after features are written.
"""

from prefect import task
from app.services.prediction_service import run_inference_for_race
from app.core.logging import get_logger

logger = get_logger(__name__)


@task(
    name="run_inference",
    retries=2,
    retry_delay_seconds=30,
    description="Run inference on latest features and store predictions",
)
def run_inference_task(race_key: str) -> dict:
    return run_inference_for_race(race_key)