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
    

    def get_driver_standings(
        self, year: int, round_number: Optional[int] = None
    ) -> pd.DataFrame:
        """
        Fetch driver championship standings.
        If round_number is omitted, returns standings after the final round.
        """
        path = (
            f"/{year}/{round_number}/driverStandings.json"
            if round_number
            else f"/{year}/driverStandings.json"
        )
        data = self._get(path)
        standings_lists = self._extract_races(data, "StandingsTable", "StandingsLists")
 
        if not standings_lists:
            return pd.DataFrame()
 
        rows = []
        for entry in standings_lists[0]["DriverStandings"]:
            rows.append({
                "driver_code": entry["Driver"].get("code", entry["Driver"]["driverId"][:3].upper()),
                "driver_id": entry["Driver"]["driverId"],
                "driver_name": f"{entry['Driver']['givenName']} {entry['Driver']['familyName']}",
                "team": entry["Constructors"][0]["name"] if entry["Constructors"] else "",
                "position": int(entry["position"]),
                "points": float(entry["points"]),
                "wins": int(entry["wins"]),
                "year": year,
                "round": round_number,
                "source": "ergast",
            })
 
        return pd.DataFrame(rows)
    

    def get_constructor_standings(
        self, year: int, round_number: Optional[int] = None
    ) -> pd.DataFrame:
        """Fetch constructor championship standings."""
        path = (
            f"/{year}/{round_number}/constructorStandings.json"
            if round_number
            else f"/{year}/constructorStandings.json"
        )
        data = self._get(path)
        standings_lists = self._extract_races(data, "StandingsTable", "StandingsLists")
 
        if not standings_lists:
            return pd.DataFrame()
 
        rows = []
        for entry in standings_lists[0]["ConstructorStandings"]:
            rows.append({
                "team_id": entry["Constructor"]["constructorId"],
                "team": entry["Constructor"]["name"],
                "position": int(entry["position"]),
                "points": float(entry["points"]),
                "wins": int(entry["wins"]),
                "year": year,
                "round": round_number,
                "source": "ergast",
            })
 
        return pd.DataFrame(rows)
    

    # ------------------------------------------------------------------
    # Internal request machinery
    # ------------------------------------------------------------------
 
    def _get(self, path: str) -> dict:
        url = f"{self.base_url}{path}"
        last_exc: Exception | None = None
 
        for attempt in range(1, _MAX_RETRIES + 1):
            try:
                logger.info(f"GET {url} attempt={attempt}")
                resp = self._session.get(url, timeout=_TIMEOUT)
 
                if resp.status_code == 429:
                    wait = _BACKOFF_BASE * (2 ** (attempt - 1))
                    logger.warning(f"Ergast rate limited — waiting {wait}s")
                    time.sleep(wait)
                    last_exc = Exception("429 rate limited")
                    continue
 
                resp.raise_for_status()
                return resp.json()
 
            except requests.exceptions.Timeout as e:
                last_exc = e
                logger.warning(f"Timeout on attempt {attempt}: {url}")
            except requests.exceptions.HTTPError as e:
                raise IngestionError(
                    "ergast", f"HTTP {e.response.status_code}: {url}"
                ) from e
            except Exception as e:
                last_exc = e
                logger.warning(f"Request error attempt {attempt}: {e}")
 
            if attempt < _MAX_RETRIES:
                time.sleep(_BACKOFF_BASE * (2 ** (attempt - 1)))
 
        raise IngestionError(
            "ergast",
            f"All {_MAX_RETRIES} attempts failed for {url}: {last_exc}",
        ) from last_exc
 
    @staticmethod
    def _extract_races(data: dict, table_key: str, list_key: str) -> list:
        """Safely extract the nested list from an Ergast MRData response."""
        try:
            return data["MRData"][table_key][list_key]
        except (KeyError, TypeError):
            return []