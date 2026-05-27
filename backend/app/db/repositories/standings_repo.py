"""
StandingsRepository

Caches driver and constructor standings fetched from Ergast.
Written by post_race_flow, read by the standings API route.
Conflict key per-year so only latest round's standings survive per season.
"""

from datetime import datetime, timezone

import pandas as pd
from sqlalchemy import text

from app.core.exceptions import StorageError
from app.core.logging import get_logger
from app.db.session import get_session

logger = get_logger(__name__)


class StandingsRepository:

    def upsert_driver_standings(self, df: pd.DataFrame) -> int:
        if df is None or df.empty:
            return 0

        stmt = text("""
            INSERT INTO driver_standings_cache (
                year, round, driver_code, driver_id, driver_name,
                team, position, points, wins, synced_at
            ) VALUES (
                :year, :round, :driver_code, :driver_id, :driver_name,
                :team, :position, :points, :wins, :synced_at
            )
            ON CONFLICT (year, driver_code)
            DO UPDATE SET
                round       = EXCLUDED.round,
                driver_name = EXCLUDED.driver_name,
                team        = EXCLUDED.team,
                position    = EXCLUDED.position,
                points      = EXCLUDED.points,
                wins        = EXCLUDED.wins,
                synced_at   = EXCLUDED.synced_at
        """)

        rows = self._prepare(df)
        try:
            with get_session() as session:
                session.execute(stmt, rows)
            logger.info(f"Upserted {len(rows)} driver standings rows")
            return len(rows)
        except Exception as e:
            raise StorageError("driver_standings_cache", str(e)) from e
        

    def upsert_constructor_standings(self, df: pd.DataFrame) -> int:
        if df is None or df.empty:
            return 0

        stmt = text("""
            INSERT INTO constructor_standings_cache (
                year, round, team_id, team, position, points, wins, synced_at
            ) VALUES (
                :year, :round, :team_id, :team, :position, :points, :wins, :synced_at
            )
            ON CONFLICT (year, team_id)
            DO UPDATE SET
                round     = EXCLUDED.round,
                team      = EXCLUDED.team,
                position  = EXCLUDED.position,
                points    = EXCLUDED.points,
                wins      = EXCLUDED.wins,
                synced_at = EXCLUDED.synced_at
        """)

        rows = self._prepare(df)
        try:
            with get_session() as session:
                session.execute(stmt, rows)
            logger.info(f"Upserted {len(rows)} constructor standings rows")
            return len(rows)
        except Exception as e:
            raise StorageError("constructor_standings_cache", str(e)) from e
        

    def get_driver_standings(self, year: int) -> pd.DataFrame:
        with get_session() as session:
            result = session.execute(text("""
                SELECT driver_code, driver_name, team, position, points, wins, round
                FROM driver_standings_cache
                WHERE year = :year
                ORDER BY position ASC
            """), {"year": year})
            rows = result.mappings().all()
        return pd.DataFrame(rows)

    def get_constructor_standings(self, year: int) -> pd.DataFrame:
        with get_session() as session:
            result = session.execute(text("""
                SELECT team_id, team, position, points, wins, round
                FROM constructor_standings_cache
                WHERE year = :year
                ORDER BY position ASC
            """), {"year": year})
            rows = result.mappings().all()
        return pd.DataFrame(rows)

    def latest_year(self) -> int | None:
        with get_session() as session:
            result = session.execute(text(
                "SELECT MAX(year) FROM driver_standings_cache"
            ))
            return result.scalar()