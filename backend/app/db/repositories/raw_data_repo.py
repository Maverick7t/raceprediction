"""
RawDataRepository — SQLAlchemy implementation.
 
All writes use INSERT ... ON CONFLICT DO UPDATE (upsert).
This keeps every pipeline run idempotent.
 
Conflict keys:
  qualifying_raw   → (race_key, driver_code)
  results_raw      → (race_key, driver_code)
  telemetry_raw    → (race_key, driver_code, lap_number)
  validation_failures → append-only, no conflict key
"""
 
from datetime import datetime, timezone
 
import pandas as pd
from sqlalchemy import text
from sqlalchemy.orm import Session
 
from app.core.exceptions import StorageError
from app.core.logging import get_logger
from app.db.session import get_session
 
logger = get_logger(__name__)
 
_BATCH_SIZE = 500
 
 
class RawDataRepository:
 
    # ------------------------------------------------------------------
    # Public upsert methods
    # ------------------------------------------------------------------
 
    def upsert_qualifying(self, df: pd.DataFrame) -> int:
        """
        Upsert qualifying rows.
        On conflict (race_key, driver_code): update all mutable columns.
        """
        if df is None or df.empty:
            logger.warning("upsert_qualifying called with empty DataFrame")
            return 0
 
        stmt = text("""
            INSERT INTO qualifying_raw (
                race_key, driver_code, driver_id, driver_name,
                team, team_id, position, q1_time, q2_time, q3_time,
                best_lap_seconds, year, round, race_name, circuit_id,
                source, ingested_at
            ) VALUES (
                :race_key, :driver_code, :driver_id, :driver_name,
                :team, :team_id, :position, :q1_time, :q2_time, :q3_time,
                :best_lap_seconds, :year, :round, :race_name, :circuit_id,
                :source, :ingested_at
            )
            ON CONFLICT (race_key, driver_code)
            DO UPDATE SET
                position         = EXCLUDED.position,
                q1_time          = EXCLUDED.q1_time,
                q2_time          = EXCLUDED.q2_time,
                q3_time          = EXCLUDED.q3_time,
                best_lap_seconds = EXCLUDED.best_lap_seconds,
                team             = EXCLUDED.team,
                source           = EXCLUDED.source,
                ingested_at      = EXCLUDED.ingested_at
        """)
 
        return self._execute_batch(df, stmt, "qualifying_raw")