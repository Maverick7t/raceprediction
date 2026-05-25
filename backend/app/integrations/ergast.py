"""
Ergast / Jolpica REST client.
 
Ergast is the authoritative source for:
  - Race results (final classification)
  - Qualifying results (positions, Q1/Q2/Q3 times)
  - Driver and constructor standings
 
Rate limiting: Ergast enforces ~200 requests per hour.
This client uses exponential backoff on 429 responses and
a conservative per-request timeout of 10 seconds.
 
Base URL is configurable via ERGAST_BASE_URL env var.
Jolpica (https://api.jolpi.ca/ergast) is the recommended host —
it is a maintained fork of the original Ergast service.
"""
 
import time
from typing import Optional
 
import pandas as pd
import requests
 
from app.core.config import config
from app.core.exceptions import IngestionError
from app.core.logging import get_logger
 
logger = get_logger(__name__)
 
_TIMEOUT = 10        # seconds per request
_MAX_RETRIES = 3
_BACKOFF_BASE = 2.0  # seconds; doubles per retry: 2s, 4s, 8s
 
 
class ErgastClient:
 
    def __init__(self, base_url: str = None):
        self.base_url = (base_url or config.ERGAST_BASE_URL).rstrip("/")
        self._session = requests.Session()
        self._session.headers.update({"Accept": "application/json"})


        # ------------------------------------------------------------------
    # Public methods
    # ------------------------------------------------------------------
 
    def get_race_results(self, year: int, round_number: int) -> pd.DataFrame:
        """
        Fetch final race classification for a given round.
        Returns one row per driver.
        """
        data = self._get(f"/{year}/{round_number}/results.json?limit=30")
        races = self._extract_races(data, "RaceTable", "Races")
 
        if not races:
            raise IngestionError(
                "ergast", f"No race results for year={year} round={round_number}"
            )
 
        race = races[0]
        race_key = _build_race_key(race["raceName"], year)
        rows = []
 
        for r in race["Results"]:
            rows.append({
                "driver_code": r["Driver"].get("code", r["Driver"]["driverId"][:3].upper()),
                "driver_id": r["Driver"]["driverId"],
                "driver_name": f"{r['Driver']['givenName']} {r['Driver']['familyName']}",
                "team": r["Constructor"]["name"],
                "team_id": r["Constructor"]["constructorId"],
                "grid_position": int(r.get("grid", 0)),
                "finish_position": int(r["position"]),
                "points": float(r.get("points", 0)),
                "status": r.get("status", ""),
                "year": year,
                "round": round_number,
                "race_key": race_key,
                "race_name": race["raceName"],
                "circuit_id": race["Circuit"]["circuitId"],
                "source": "ergast",
            })
 
        logger.info(f"Ergast race results: {len(rows)} rows year={year} round={round_number}")
        return pd.DataFrame(rows)
    

    def get_qualifying_results(self, year: int, round_number: int) -> pd.DataFrame:
        """
        Fetch qualifying classification for a given round.
        Returns one row per driver with Q1/Q2/Q3 times as strings.
        Q2 and Q3 are nullable — not all drivers reach those segments.
        """
        data = self._get(f"/{year}/{round_number}/qualifying.json?limit=30")
        races = self._extract_races(data, "RaceTable", "Races")
 
        if not races:
            raise IngestionError(
                "ergast", f"No qualifying results for year={year} round={round_number}"
            )
 
        race = races[0]
        race_key = _build_race_key(race["raceName"], year)
        rows = []
 
        for r in race["QualifyingResults"]:
            rows.append({
                "driver_code": r["Driver"].get("code", r["Driver"]["driverId"][:3].upper()),
                "driver_id": r["Driver"]["driverId"],
                "driver_name": f"{r['Driver']['givenName']} {r['Driver']['familyName']}",
                "team": r["Constructor"]["name"],
                "team_id": r["Constructor"]["constructorId"],
                "position": int(r["position"]),
                "q1_time": r.get("Q1") or None,
                "q2_time": r.get("Q2") or None,
                "q3_time": r.get("Q3") or None,
                "year": year,
                "round": round_number,
                "race_key": race_key,
                "race_name": race["raceName"],
                "circuit_id": race["Circuit"]["circuitId"],
                "source": "ergast",
            })
 
        logger.info(f"Ergast qualifying: {len(rows)} rows year={year} round={round_number}")
        return pd.DataFrame(rows)