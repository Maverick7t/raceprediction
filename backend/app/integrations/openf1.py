"""
OpenF1 integration client.

OpenF1 is supplementary — newer API, occasionally incomplete.
Every method in this client is designed to return an empty DataFrame
rather than raise on failure. Callers do not need try/except blocks.

Used for: pit stop durations, stint data.
These enrich the telemetry tables but are not required for inference.
"""

import time

import pandas as pd
import requests

from app.core.config import config
from app.core.logging import get_logger

logger = get_logger(__name__)

_TIMEOUT = 10
_MAX_RETRIES = 3


class OpenF1Client:

    def __init__(self, base_url: str = None):
        self.base_url = (base_url or config.OPENF1_BASE_URL).rstrip("/")
        self._session = requests.Session()

    def get_pit_stops(self, year: int, round_number: int) -> pd.DataFrame:
        """
        Fetch pit stop data for a race.
        Returns empty DataFrame on any failure — always non-fatal.
        """
        try:
            session_key = self._resolve_session_key(year, round_number, "Race")
            if not session_key:
                logger.warning(f"OpenF1: no session_key found year={year} round={round_number}")
                return pd.DataFrame()

            data = self._get(f"/pit?session_key={session_key}")
            if not data:
                return pd.DataFrame()

            rows = [
                {
                    "driver_number": pit.get("driver_number"),
                    "lap_number": pit.get("lap_number"),
                    "pit_duration_seconds": pit.get("pit_duration"),
                    "session_key": session_key,
                    "year": year,
                    "round": round_number,
                    "source": "openf1",
                }
                for pit in data
            ]

            logger.info(f"OpenF1 pit stops: {len(rows)} rows year={year} round={round_number}")
            return pd.DataFrame(rows)

        except Exception as e:
            logger.warning(f"OpenF1 get_pit_stops failed (non-fatal): {e}")
            return pd.DataFrame()

    def get_stints(self, year: int, round_number: int) -> pd.DataFrame:
        """
        Fetch stint and compound data for a race.
        Returns empty DataFrame on any failure.
        """
        try:
            session_key = self._resolve_session_key(year, round_number, "Race")
            if not session_key:
                return pd.DataFrame()

            data = self._get(f"/stints?session_key={session_key}")
            if not data:
                return pd.DataFrame()

            rows = [
                {
                    "driver_number": s.get("driver_number"),
                    "stint_number": s.get("stint_number"),
                    "compound": s.get("compound"),
                    "lap_start": s.get("lap_start"),
                    "lap_end": s.get("lap_end"),
                    "tyre_age_at_start": s.get("tyre_age_at_start"),
                    "session_key": session_key,
                    "year": year,
                    "round": round_number,
                    "source": "openf1",
                }
                for s in data
            ]

            logger.info(f"OpenF1 stints: {len(rows)} rows year={year} round={round_number}")
            return pd.DataFrame(rows)

        except Exception as e:
            logger.warning(f"OpenF1 get_stints failed (non-fatal): {e}")
            return pd.DataFrame()

    # ------------------------------------------------------------------
    # Internal
    # ------------------------------------------------------------------

    def _resolve_session_key(
        self, year: int, round_number: int, session_type: str
    ) -> str | None:
        """
        Resolve a numeric session_key from year + round + session_type.
        OpenF1 uses session_key as its primary identifier, not year/round.
        Returns None if the session cannot be resolved.
        """
        try:
            data = self._get(f"/sessions?year={year}&session_name={session_type}")
            if not data:
                return None
            # Sessions are returned in order; match by round index heuristic
            if len(data) >= round_number:
                return str(data[round_number - 1].get("session_key", ""))
            return str(data[-1].get("session_key", ""))
        except Exception as e:
            logger.warning(f"OpenF1 session key resolution failed: {e}")
            return None

    def _get(self, path: str) -> list:
        url = f"{self.base_url}{path}"
        for attempt in range(1, _MAX_RETRIES + 1):
            try:
                resp = self._session.get(url, timeout=_TIMEOUT)
                resp.raise_for_status()
                return resp.json()
            except Exception:
                if attempt == _MAX_RETRIES:
                    raise
                time.sleep(2 ** attempt)
        return []