"""
Post-qualifying ingestion flow. (Phase 4 update — adds inference step.)
"""

from prefect import flow, get_run_logger
from app.core.sentry import init_sentry, set_sentry_context

from workers.tasks.fetch_tasks import fetch_qualifying_ergast, fetch_qualifying_fastf1
from workers.tasks.store_tasks import store_qualifying_raw
from workers.tasks.validate_tasks import validate_qualifying
from workers.tasks.inference_tasks import run_inference_task
from workers.flows.feature_engineering_flow import feature_engineering_flow


@flow(
    name="post_qualifying_ingestion",
    description="Ingest qualifying data and generate race predictions",
    log_prints=True,
)
def post_qualifying_flow(year: int, round_number: int) -> dict:
    init_sentry()
    set_sentry_context(flow_name="post_qualifying_flow")
    run_logger = get_run_logger()
    run_logger.info(f"post_qualifying_flow started year={year} round={round_number}")

    # Step 1: Ergast (authoritative)
    ergast_df = fetch_qualifying_ergast(year, round_number)
    race_key = (
        ergast_df["race_key"].iloc[0]
        if not ergast_df.empty
        else f"unknown_{year}_{round_number}"
    )

    # Step 2: FastF1 lap time enrichment (non-fatal)
    try:
        fastf1_df = fetch_qualifying_fastf1(year, round_number)
        lap_cols = ["driver_code", "race_key", "best_lap_seconds"]
        available = [c for c in lap_cols if c in fastf1_df.columns]
        if "best_lap_seconds" in fastf1_df.columns:
            merged_df = ergast_df.merge(fastf1_df[available], on=["driver_code", "race_key"], how="left")
            run_logger.info("FastF1 lap times merged")
        else:
            merged_df = ergast_df
    except Exception as exc:
        run_logger.warning(f"FastF1 fetch failed — Ergast only. Error: {exc}")
        merged_df = ergast_df

    # Step 3: Validate + store
    validated_df = validate_qualifying(merged_df, race_key)
    rows_stored = store_qualifying_raw(validated_df)

    # Step 4: Feature engineering
    feature_result = feature_engineering_flow(race_key, year, round_number)
    run_logger.info(f"Features computed: {feature_result}")

    # Step 5: Inference → predictions table
    inference_result = run_inference_task(race_key)
    run_logger.info(f"Inference complete: {inference_result}")

    return {
        "race_key": race_key,
        "rows_stored": rows_stored,
        "year": year,
        "round": round_number,
        "features": feature_result,
        "inference": inference_result,
    }


if __name__ == "__main__":
    import sys
    year = int(sys.argv[1]) if len(sys.argv) > 1 else 2024
    round_num = int(sys.argv[2]) if len(sys.argv) > 2 else 1
    result = post_qualifying_flow(year, round_num)
    print(result)