"""
Post-race ingestion flow.
 
Triggered: Sunday after the race finishes (via GitHub Actions workflow).
 
Responsibilities:
  1. Fetch final race classification from Ergast
  2. Fetch race lap telemetry from FastF1
  3. Fetch pit stop data from OpenF1 (supplementary only)
  4. Validate and store results_raw and telemetry_raw
  5. Fetch and store updated driver + constructor standings
 
Graceful degradation:
  - Ergast results: REQUIRED. Flow fails hard if this fails.
  - FastF1 telemetry: OPTIONAL. Flow logs warning and continues.
  - OpenF1 pit stops: OPTIONAL. Always returns empty df on failure.
  - Standings: OPTIONAL. Standings are updated by a separate cron job too.
 
After this flow completes, the post-race ML training trigger
checks if enough new results have accumulated to warrant retraining.
That check is in Phase 3 and is invoked as a separate flow.
"""
 
from prefect import flow, get_run_logger
 
from workers.tasks.fetch_tasks import (
    fetch_constructor_standings,
    fetch_driver_standings,
    fetch_pit_stops,
    fetch_race_results,
    fetch_race_telemetry,
)
from workers.tasks.store_tasks import store_results_raw, store_telemetry_raw
from workers.tasks.validate_tasks import validate_results, validate_telemetry
 
 
@flow(
    name="post_race_ingestion",
    description="Ingest race results and telemetry after a Sunday race",
    log_prints=True,
)
def post_race_flow(year: int, round_number: int) -> dict:
    """
    Args:
        year:         Championship year (e.g. 2025)
        round_number: Race round number within the season (1-based)
 
    Returns:
        Summary dict with counts for downstream logging and Phase 3 trigger.
    """
    run_logger = get_run_logger()
    run_logger.info(f"post_race_flow started year={year} round={round_number}")