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
from prefect.tasks import exponential_backoff
 
from app.integrations.ergast import ErgastClient
from app.integrations.fastf1_client import load_qualifying_session, load_race_telemetry
from app.integrations.openf1 import OpenF1Client
from app.core.logging import get_logger
 
logger = get_logger(__name__)
 
_ergast = ErgastClient()
_openf1 = OpenF1Client()
 
 
@task(
    name="fetch_qualifying_ergast",
    retries=3,
    retry_delay_seconds=exponential_backoff(backoff_factor=2),
    description="Fetch qualifying classification from Ergast/Jolpica",
)
def fetch_qualifying_ergast(year: int, round_number: int) -> pd.DataFrame:
    return _ergast.get_qualifying_results(year, round_number)

@task(
    name="fetch_qualifying_fastf1",
    retries=3,
    retry_delay_seconds=exponential_backoff(backoff_factor=2),
    description="Fetch qualifying lap times from FastF1 (enriches Ergast data)",
)
def fetch_qualifying_fastf1(year: int, round_number: int) -> pd.DataFrame:
    return load_qualifying_session(year, round_number)

@task(
    name="fetch_race_results",
    retries=3,
    retry_delay_seconds=exponential_backoff(backoff_factor=2),
    description="Fetch final race classification from Ergast",
)
def fetch_race_results(year: int, round_number: int) -> pd.DataFrame:
    return _ergast.get_race_results(year, round_number)
 
 
@task(
    name="fetch_race_telemetry",
    retries=3,
    retry_delay_seconds=exponential_backoff(backoff_factor=2),
    description="Fetch race lap-level telemetry from FastF1",
)
def fetch_race_telemetry(year: int, round_number: int) -> pd.DataFrame:
    return load_race_telemetry(year, round_number)