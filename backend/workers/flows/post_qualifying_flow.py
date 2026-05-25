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

def post_qualifying_flow(year: int, round_number: int) -> dict:
    """
    Args:
        year:         Championship year (e.g. 2025)
        round_number: Race round number within the season (1-based)
 
    Returns:
        Dict with race_key and rows_stored for downstream logging.
    """
    run_logger = get_run_logger()
    run_logger.info(f"post_qualifying_flow started year={year} round={round_number}")
 
    # Step 1: Ergast is authoritative for qualifying positions and metadata.
    # This task raises on failure — no Ergast means no qualifying data.
    ergast_df = fetch_qualifying_ergast(year, round_number)
 
    race_key = (
        ergast_df["race_key"].iloc[0]
        if not ergast_df.empty
        else f"unknown_{year}_{round_number}"
    )

    # Step 2: FastF1 enriches with lap time detail.
    # Wrapped in try/except at flow level — FastF1 failure is non-fatal.
    try:
        fastf1_df = fetch_qualifying_fastf1(year, round_number)
 
        # Merge: Ergast is the base (has full driver metadata).
        # FastF1 contributes best_lap_seconds only.
        lap_time_cols = ["driver_code", "race_key", "best_lap_seconds"]
        available_cols = [c for c in lap_time_cols if c in fastf1_df.columns]
 
        if "best_lap_seconds" in fastf1_df.columns:
            merged_df = ergast_df.merge(
                fastf1_df[available_cols],
                on=["driver_code", "race_key"],
                how="left",
            )
            run_logger.info("FastF1 lap times merged successfully")
        else:
            merged_df = ergast_df
            run_logger.warning("FastF1 data missing best_lap_seconds column — skipping merge")
 
    except Exception as exc:
        run_logger.warning(
            f"FastF1 fetch failed — continuing with Ergast data only. Error: {exc}"
        )
        merged_df = ergast_df

    # Step 3: Validate. Invalid rows go to validation_failures audit table.
    validated_df = validate_qualifying(merged_df, race_key)
 
    # Step 4: Upsert to Supabase.
    rows_stored = store_qualifying_raw(validated_df)
 
    run_logger.info(
        f"post_qualifying_flow complete race_key={race_key} rows_stored={rows_stored}"
    )
 
    return {
        "race_key": race_key,
        "rows_stored": rows_stored,
        "year": year,
        "round": round_number,
    }
 
 
# Allow direct invocation for local testing:
#   python -m workers.flows.post_qualifying_flow
if __name__ == "__main__":
    import sys
    year = int(sys.argv[1]) if len(sys.argv) > 1 else 2024
    round_num = int(sys.argv[2]) if len(sys.argv) > 2 else 1
    result = post_qualifying_flow(year, round_num)
    print(result)