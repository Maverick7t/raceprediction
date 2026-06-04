# scripts/backfill_standings.py
import sys
import os
from app.integrations.ergast import ErgastClient
from app.db.repositories.standings_repo import StandingsRepository
from app.core.logging import get_logger


from dotenv import load_dotenv
load_dotenv()
sys.path.insert(0, os.path.dirname(os.path.dirname(__file__)))


logger = get_logger(__name__)
ergast = ErgastClient()
repo = StandingsRepository()


YEARS = [2021, 2022, 2023, 2025]

for year in YEARS:
    try:
        driver_df = ergast.get_driver_standings(year)
        if not driver_df.empty:
            driver_df["year"] = year
            count = repo.upsert_driver_standings(driver_df)
            logger.info(f"{year} drivers: {count} rows")
    except Exception as e:
        logger.error(f"{year} driver standings failed: {e}")

    try:
        constructor_df = ergast.get_constructor_standings(year)
        if not constructor_df.empty:
            constructor_df["year"] = year
            count = repo.upsert_constructor_standings(constructor_df)
            logger.info(f"{year} constructors: {count} rows")
    except Exception as e:
        logger.error(f"{year} constructor standings failed: {e}")