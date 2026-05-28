"""
Prefect fetch tasks.
 
Each task wraps exactly one external API call.
Retry policy: 3 attempts, exponential backoff (2s, 4s, 8s).
OpenF1 tasks use 2 retries only — OpenF1 is supplementary.
 
Task granularity is intentional: if FastF1 fails, Ergast can still succeed.
Prefect retries each task independently, not the whole flow.
"""
 
import pandas as pd
from prefect import task
 
from app.integrations.ergast import ErgastClient
from app.integrations.fastf1_client import load_qualifying_session, load_race_telemetry
from app.integrations.openf1 import OpenF1Client
from app.core.logging import get_logger
 
logger = get_logger(__name__)
 
_ergast = ErgastClient()
_openf1 = OpenF1Client()
BACKOFF_SEQUENCE = [2, 4, 8]
 
 
@task(
    name="fetch_qualifying_ergast",
    retries=3,
    retry_delay_seconds=BACKOFF_SEQUENCE,
    description="Fetch qualifying classification from Ergast/Jolpica",
)
def fetch_qualifying_ergast(year: int, round_number: int) -> pd.DataFrame:
    return _ergast.get_qualifying_results(year, round_number)

@task(
    name="fetch_qualifying_fastf1",
    retries=3,
    retry_delay_seconds=BACKOFF_SEQUENCE,
    description="Fetch qualifying lap times from FastF1 (enriches Ergast data)",
)
def fetch_qualifying_fastf1(year: int, round_number: int) -> pd.DataFrame:
    return load_qualifying_session(year, round_number)

@task(
    name="fetch_race_results",
    retries=3,
    retry_delay_seconds=BACKOFF_SEQUENCE,
    description="Fetch final race classification from Ergast",
)
def fetch_race_results(year: int, round_number: int) -> pd.DataFrame:
    return _ergast.get_race_results(year, round_number)
 
 
@task(
    name="fetch_race_telemetry",
    retries=3,
    retry_delay_seconds=BACKOFF_SEQUENCE,
    description="Fetch race lap-level telemetry from FastF1",
)
def fetch_race_telemetry(year: int, round_number: int) -> pd.DataFrame:
    return load_race_telemetry(year, round_number)

@task(
    name="fetch_driver_standings",
    retries=3,
    retry_delay_seconds=BACKOFF_SEQUENCE,
    description="Fetch driver championship standings from Ergast",
)
def fetch_driver_standings(year: int, round_number: int) -> pd.DataFrame:
    return _ergast.get_driver_standings(year, round_number)
 
 
@task(
    name="fetch_constructor_standings",
    retries=3,
    retry_delay_seconds=BACKOFF_SEQUENCE,
    description="Fetch constructor championship standings from Ergast",
)
def fetch_constructor_standings(year: int, round_number: int) -> pd.DataFrame:
    return _ergast.get_constructor_standings(year, round_number)


@task(
    name="fetch_pit_stops_openf1",
    retries=2,
    retry_delay_seconds=10,
    description="Fetch pit stop data from OpenF1 (supplementary, non-fatal)",
)
def fetch_pit_stops(year: int, round_number: int) -> pd.DataFrame:
    """OpenF1 is optional. Returns empty DataFrame on all failures."""
    return _openf1.get_pit_stops(year, round_number)
 