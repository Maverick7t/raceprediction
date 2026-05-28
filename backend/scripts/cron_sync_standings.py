"""
scripts/cron_sync_standings.py  (also registered as a Prefect deployment)

Scheduled standing sync — runs every Monday at 06:00 UTC.

Why a cron instead of relying on post_race_flow?
  - post_race_flow fetches standings but doesn't store them to the standings
    cache tables yet (that's Phase 4's job).
  - Race weekends are the primary update path; this cron is the safety net
    that keeps standings current during sprint weekends, red-flagged races,
    and any post_race_flow failures.
  - Off-season: this keeps the final standings visible all winter.

Flow steps:
  1. Determine the current year
  2. Fetch driver standings from Ergast (final round = latest)
  3. Fetch constructor standings from Ergast
  4. Upsert both into standings cache tables
  5. Log row counts + any failures to Sentry

Idempotency: standings tables use UPSERT ON CONFLICT (year, driver_code)
so running this multiple times per day is safe.
"""

from __future__ import annotations

import sys
from datetime import datetime, timezone

from prefect import flow, task, get_run_logger

from app.core.sentry import init_sentry, capture_exception, set_sentry_context
from app.core.logging import get_logger
from app.integrations.ergast import ErgastClient
from app.db.repositories.standings_repo import StandingsRepository

logger = get_logger(__name__)
_ergast = ErgastClient()
_standings_repo = StandingsRepository()
BACKOFF_SEQUENCE = [2, 4, 8]


# ---------------------------------------------------------------------------
# Tasks
# ---------------------------------------------------------------------------

@task(
    name="fetch_driver_standings_cron",
    retries=3,
    retry_delay_seconds=BACKOFF_SEQUENCE,
    description="Fetch current driver championship standings from Ergast",
)
def fetch_driver_standings_task(year: int):
    df = _ergast.get_driver_standings(year)
    logger.info(f"Fetched {len(df)} driver standing rows year={year}")
    return df


@task(
    name="fetch_constructor_standings_cron",
    retries=3,
    retry_delay_seconds=BACKOFF_SEQUENCE,
    description="Fetch current constructor championship standings from Ergast",
)
def fetch_constructor_standings_task(year: int):
    df = _ergast.get_constructor_standings(year)
    logger.info(f"Fetched {len(df)} constructor standing rows year={year}")
    return df


@task(
    name="store_driver_standings_cron",
    retries=2,
    retry_delay_seconds=10,
    description="Upsert driver standings into driver_standings_cache",
)
def store_driver_standings_task(df, year: int) -> int:
    if df is None or df.empty:
        logger.warning(f"No driver standings to store for year={year}")
        return 0
    count = _standings_repo.upsert_driver_standings(df)
    logger.info(f"Stored {count} driver standing rows year={year}")
    return count


@task(
    name="store_constructor_standings_cron",
    retries=2,
    retry_delay_seconds=10,
    description="Upsert constructor standings into constructor_standings_cache",
)
def store_constructor_standings_task(df, year: int) -> int:
    if df is None or df.empty:
        logger.warning(f"No constructor standings to store for year={year}")
        return 0
    count = _standings_repo.upsert_constructor_standings(df)
    logger.info(f"Stored {count} constructor standing rows year={year}")
    return count

# ---------------------------------------------------------------------------
# Flow
# ---------------------------------------------------------------------------

@flow(
    name="cron_sync_standings",
    description="Sync F1 championship standings — runs every Monday 06:00 UTC",
    log_prints=True,
)
def cron_sync_standings_flow(year: int | None = None) -> dict:
    """
    Args:
        year: Season to sync. Defaults to current calendar year.
              Pass explicitly to back-fill a previous season.
    """
    init_sentry()
    run_logger = get_run_logger()

    target_year = year or datetime.now(timezone.utc).year
    set_sentry_context(flow_name="cron_sync_standings")
    run_logger.info(f"cron_sync_standings started year={target_year}")

    driver_rows_stored = 0
    constructor_rows_stored = 0
    errors = []

    # Driver standings — non-fatal on failure; last stored values remain
    try:
        driver_df = fetch_driver_standings_task(target_year)
        driver_rows_stored = store_driver_standings_task(driver_df, target_year)
    except Exception as exc:
        msg = f"Driver standings sync failed: {exc}"
        run_logger.error(msg)
        capture_exception(exc, year=target_year, flow="cron_sync_standings")
        errors.append(msg)

    # Constructor standings — non-fatal on failure
    try:
        constructor_df = fetch_constructor_standings_task(target_year)
        constructor_rows_stored = store_constructor_standings_task(
            constructor_df, target_year
        )
    except Exception as exc:
        msg = f"Constructor standings sync failed: {exc}"
        run_logger.error(msg)
        capture_exception(exc, year=target_year, flow="cron_sync_standings")
        errors.append(msg)

    result = {
        "year": target_year,
        "driver_rows_stored": driver_rows_stored,
        "constructor_rows_stored": constructor_rows_stored,
        "errors": errors,
        "status": "partial_failure" if errors else "completed",
    }

    run_logger.info(f"cron_sync_standings complete: {result}")
    return result


if __name__ == "__main__":
    year_arg = int(sys.argv[1]) if len(sys.argv) > 1 else None
    result = cron_sync_standings_flow(year=year_arg)
    logger.info(f"Cron completed result={result}")
