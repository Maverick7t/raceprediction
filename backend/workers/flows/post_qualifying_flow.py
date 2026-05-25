"""
Post-qualifying ingestion flow.
 
Triggered: Saturday after qualifying session (via GitHub Actions workflow).
 
Responsibilities:
  1. Fetch qualifying classification from Ergast (authoritative for positions)
  2. Fetch qualifying lap times from FastF1 (enriches with best_lap_seconds)
  3. Merge both sources — Ergast is the base, FastF1 enriches it
  4. Validate merged DataFrame against QualifyingRawSchema
  5. Upsert to qualifying_raw
 
Graceful degradation:
  If FastF1 fetch fails after all retries, the flow continues with
  Ergast data only. best_lap_seconds will be null for all rows.
  This is acceptable — Ergast positions are sufficient for inference.
  The failure is logged as a warning, not an error.
 
  If Ergast fails, the flow fails hard — there is no fallback for
  the authoritative classification data.
"""
 
from prefect import flow, get_run_logger
 
from workers.tasks.fetch_tasks import (
    fetch_qualifying_ergast,
    fetch_qualifying_fastf1,
)
from workers.tasks.store_tasks import store_qualifying_raw
from workers.tasks.validate_tasks import validate_qualifying
 
 
@flow(
    name="post_qualifying_ingestion",
    description="Ingest qualifying data after a Saturday qualifying session",
    log_prints=True,
)

