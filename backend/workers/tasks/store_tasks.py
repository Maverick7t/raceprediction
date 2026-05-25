"""
Prefect store tasks.
 
These are intentionally thin — each task calls exactly one repository method.
No business logic lives here. The repository owns the upsert logic.
 
Keeping store tasks separate from fetch/validate tasks means Prefect
can retry storage independently. If Supabase has a transient outage,
only the store task retries — not the fetch.
"""
 
import pandas as pd
from prefect import task
 
from app.core.logging import get_logger
from app.db.repositories.raw_data_repo import RawDataRepository
 
logger = get_logger(__name__)
_repo = RawDataRepository()
 
 
@task(
    name="store_qualifying_raw",
    retries=2,
    retry_delay_seconds=10,
    description="Upsert qualifying rows into qualifying_raw table",
)
def store_qualifying_raw(df: pd.DataFrame) -> int:
    count = _repo.upsert_qualifying(df)
    logger.info(f"store_qualifying_raw: {count} rows written")
    return count

@task(
    name="store_results_raw",
    retries=2,
    retry_delay_seconds=10,
    description="Upsert race result rows into results_raw table",
)
def store_results_raw(df: pd.DataFrame) -> int:
    count = _repo.upsert_results(df)
    logger.info(f"store_results_raw: {count} rows written")
    return count
 
 
@task(
    name="store_telemetry_raw",
    retries=2,
    retry_delay_seconds=10,
    description="Upsert lap telemetry rows into telemetry_raw table",
)
def store_telemetry_raw(df: pd.DataFrame) -> int:
    count = _repo.upsert_telemetry(df)
    logger.info(f"store_telemetry_raw: {count} rows written")
    return count