"""
Feature engineering Prefect flow.

Triggered twice per race weekend:
  1. Saturday after qualifying → session features populated, targets null
  2. Sunday after race → targets (finish_position, is_winner, is_podium) filled

Both runs are idempotent — re-running overwrites existing rows via upsert.
"""

import sys
from prefect import flow, task, get_run_logger
from app.core.sentry import init_sentry, set_sentry_context

from app.features.compute import compute_features_for_race
from app.db.repositories.feature_repo import FeatureRepository

_repo = FeatureRepository()


@task(name="compute_features", retries=2, retry_delay_seconds=30)
def compute_features_task(race_key: str, year: int, round_number: int):
    return compute_features_for_race(race_key, year, round_number)


@task(name="store_features", retries=2, retry_delay_seconds=10)
def store_features_task(df):
    return _repo.upsert_features(df)


@flow(name="feature_engineering", log_prints=True)
def feature_engineering_flow(race_key: str, year: int, round_number: int) -> dict:
    """
    Args:
        race_key:     e.g. "bahrain_grand_prix_2024"
        year:         e.g. 2024
        round_number: e.g. 1
    """
    init_sentry()
    set_sentry_context(flow_name="feature_engineering_flow")
    logger = get_run_logger()
    logger.info(f"Feature engineering started race_key={race_key}")

    features_df = compute_features_task(race_key, year, round_number)

    if features_df.empty:
        logger.error(f"No features computed for race_key={race_key}")
        return {"race_key": race_key, "rows_stored": 0, "status": "failed"}

    rows_stored = store_features_task(features_df)

    logger.info(f"Feature engineering complete race_key={race_key} rows={rows_stored}")
    return {
        "race_key": race_key,
        "year": year,
        "round": round_number,
        "rows_stored": rows_stored,
        "status": "completed",
    }


if __name__ == "__main__":
    race_key = sys.argv[1] if len(sys.argv) > 1 else "bahrain_grand_prix_2024"
    year = int(sys.argv[2]) if len(sys.argv) > 2 else 2024
    round_num = int(sys.argv[3]) if len(sys.argv) > 3 else 1
    result = feature_engineering_flow(race_key, year, round_num)
    print(result)