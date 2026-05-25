"""
FastF1 integration client.
 
Responsibility: load qualifying and race session data from FastF1.
All DataFrame columns are normalised here before leaving this module.
Nothing outside this module imports fastf1 directly.
 
Cache behaviour:
  FastF1 writes to disk on first load. Subsequent loads for the same
  session hit the disk cache and are fast (~1s vs 30–60s cold).
  Cache dir is configurable via FASTF1_CACHE_DIR env var.
  In CI/CD, set FASTF1_CACHE_DIR to a path that is NOT in /tmp if you
  want the cache to persist across workflow runs (use a cache action).
"""
 
from pathlib import Path
 
from app.integrations.ergast import _build_race_key
import fastf1
import pandas as pd
 
from app.core.config import config
from app.core.exceptions import IngestionError
from app.core.logging import get_logger
 
logger = get_logger(__name__)
 
# Configure FastF1 cache once at import time
Path(config.FASTF1_CACHE_DIR).mkdir(parents=True, exist_ok=True)
fastf1.Cache.enable_cache(config.FASTF1_CACHE_DIR)


# ---------------------------------------------------------------------------
# Public API
# ---------------------------------------------------------------------------
 
def load_qualifying_session(year: int, round_number: int) -> pd.DataFrame:
    """
    Load qualifying session from FastF1. Returns one row per driver
    containing their best lap time in seconds and computed grid position.
 
    Raises IngestionError if the session cannot be loaded or contains no laps.
    """
    logger.info(f"FastF1: loading qualifying year={year} round={round_number}")
 
    try:
        session = fastf1.get_session(year, round_number, "Q")
        # Load laps only — telemetry/weather would slow this down significantly
        session.load(laps=True, telemetry=False, weather=False, messages=False)
    except Exception as e:
        raise IngestionError("fastf1", f"Session load failed: {e}") from e
 
    laps = session.laps
 
    if laps is None or laps.empty:
        raise IngestionError(
            "fastf1",
            f"No lap data in qualifying session year={year} round={round_number}",
        )
 
    # Keep only accurate laps (no pit lane exits, VSC outlaps etc.)
    valid_laps = laps[laps["IsAccurate"] == True].copy()
    if valid_laps.empty:
        # Fall back to all laps if IsAccurate filters everything out
        valid_laps = laps.copy()
        logger.warning("IsAccurate filtered all laps — using unfiltered set")
 
    best = (
        valid_laps.groupby("Driver")["LapTime"]
        .min()
        .reset_index()
        .rename(columns={"Driver": "driver_code", "LapTime": "best_lap_time"})
    )
 
    best["best_lap_seconds"] = best["best_lap_time"].dt.total_seconds()
    best["position"] = best["best_lap_seconds"].rank(method="min").astype(int)
 
    race_key = _build_race_key(session.event["EventName"], year)
    best["race_key"] = race_key
    best["session_name"] = session.event["EventName"]
    best["circuit"] = session.event["Location"]
    best["year"] = year
    best["round"] = round_number
    best["source"] = "fastf1"
 
    best = best.drop(columns=["best_lap_time"])
 
    logger.info(f"FastF1 qualifying: {len(best)} drivers loaded race_key={race_key}")
    return best


def load_race_telemetry(year: int, round_number: int) -> pd.DataFrame:
    """
    Load race lap data from FastF1.
    Returns one row per driver per lap with compound, tyre life, and lap time.
    Telemetry is at lap granularity — not per-sample — to keep row counts manageable.
 
    Raises IngestionError on hard failure. Caller should handle gracefully.
    """
    logger.info(f"FastF1: loading race telemetry year={year} round={round_number}")
 
    try:
        session = fastf1.get_session(year, round_number, "R")
        session.load(laps=True, telemetry=False, weather=False, messages=False)
    except Exception as e:
        raise IngestionError("fastf1", f"Race session load failed: {e}") from e
 
    laps = session.laps
 
    if laps is None or laps.empty:
        raise IngestionError(
            "fastf1",
            f"No lap data in race session year={year} round={round_number}",
        )
 
    wanted = ["Driver", "LapNumber", "LapTime", "Stint", "Compound", "TyreLife", "IsAccurate"]
    df = laps[wanted].copy()
 
    df = df.rename(columns={
        "Driver": "driver_code",
        "LapNumber": "lap_number",
        "LapTime": "lap_time",
        "Stint": "stint",
        "Compound": "compound",
        "TyreLife": "tyre_life",
        "IsAccurate": "is_accurate",
    })
 
    df["lap_seconds"] = df["lap_time"].dt.total_seconds()
 
    race_key = _build_race_key(session.event["EventName"], year)
    df["race_key"] = race_key
    df["year"] = year
    df["round"] = round_number
    df["source"] = "fastf1"
 
    df = df.drop(columns=["lap_time"])
 
    # Filter out safety car / outlap rows that have impossibly slow times
    df = df[df["lap_seconds"].isna() | (df["lap_seconds"] < 300)]
 
    logger.info(f"FastF1 telemetry: {len(df)} lap rows loaded race_key={race_key}")
    return df.reset_index(drop=True)


def get_season_schedule(year: int) -> pd.DataFrame:
    """
    Return the full event schedule for a season.
    Used by GitHub Actions to determine trigger dates.
    """
    try:
        schedule = fastf1.get_event_schedule(year, include_testing=False)
        df = schedule[["RoundNumber", "EventName", "Location", "Country", "EventDate"]].copy()
        df.columns = ["round", "event_name", "location", "country", "event_date"]
        df["year"] = year
        return df
    except Exception as e:
        raise IngestionError("fastf1", f"Schedule load failed for year={year}: {e}") from e
 

 # ---------------------------------------------------------------------------
# Internal helpers
# ---------------------------------------------------------------------------
 
def _build_race_key(event_name: str, year: int) -> str:
    """
    Produce a stable, lowercase snake_case race identifier.
    Example: "Bahrain Grand Prix" + 2024 → "bahrain_grand_prix_2024"
    This key is the join key across all raw tables.
    """
    slug = (
        event_name.lower()
        .strip()
        .replace(" ", "_")
        .replace("-", "_")
        .replace("'", "")
        .replace(".", "")
    )
    return f"{slug}_{year}"
 