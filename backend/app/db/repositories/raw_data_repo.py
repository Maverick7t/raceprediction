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
import math
import numpy as np
from sqlalchemy import text
from sqlalchemy.orm import Session
 
from app.core.exceptions import StorageError
from app.core.logging import get_logger
from app.db.session import get_session
 
logger = get_logger(__name__)
 
_BATCH_SIZE = 500


def _to_python_type(value):
    """Convert numpy/pandas scalars into plain Python types.

    Tests import this function directly.
    """
    import math
    import numpy as np

    if value is None:
        return None
    if isinstance(value, np.integer):
        return int(value)
    if isinstance(value, np.floating):
        return None if math.isnan(value) else float(value)
    if isinstance(value, np.bool_):
        return bool(value)
    if isinstance(value, float) and math.isnan(value):
        return None

    try:
        return None if pd.isna(value) else value
    except (TypeError, ValueError):
        return value
 
 
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
 
        # best_lap_seconds is optional in validation (required=False) and can be
        # missing from the DataFrame entirely; SQLAlchemy text binds still need
        # the key present in every row mapping.
        return self._execute_batch(
            df,
            stmt,
            "qualifying_raw",
            defaults={"best_lap_seconds": None},
        )
    def upsert_results(self, df: pd.DataFrame) -> int:
        """
        Upsert race result rows.
        On conflict (race_key, driver_code): update all mutable columns.
        """
        if df is None or df.empty:
            logger.warning("upsert_results called with empty DataFrame")
            return 0
 
        stmt = text("""
            INSERT INTO results_raw (
                race_key, driver_code, driver_id, driver_name,
                team, team_id, grid_position, finish_position,
                points, status, year, round, race_name,
                circuit_id, source, ingested_at
            ) VALUES (
                :race_key, :driver_code, :driver_id, :driver_name,
                :team, :team_id, :grid_position, :finish_position,
                :points, :status, :year, :round, :race_name,
                :circuit_id, :source, :ingested_at
            )
            ON CONFLICT (race_key, driver_code)
            DO UPDATE SET
                finish_position = EXCLUDED.finish_position,
                grid_position   = EXCLUDED.grid_position,
                points          = EXCLUDED.points,
                status          = EXCLUDED.status,
                team            = EXCLUDED.team,
                source          = EXCLUDED.source,
                ingested_at     = EXCLUDED.ingested_at
        """)
 
        return self._execute_batch(df, stmt, "results_raw")
    
    def upsert_telemetry(self, df: pd.DataFrame) -> int:
        """
        Upsert telemetry rows.
        On conflict (race_key, driver_code, lap_number): update lap data.
        Large tables — batched at 500 rows.
        """
        if df is None or df.empty:
            logger.warning("upsert_telemetry called with empty DataFrame")
            return 0
 
        stmt = text("""
            INSERT INTO telemetry_raw (
                race_key, driver_code, lap_number, lap_seconds,
                stint, compound, tyre_life, is_accurate,
                year, round, source, ingested_at
            ) VALUES (
                :race_key, :driver_code, :lap_number, :lap_seconds,
                :stint, :compound, :tyre_life, :is_accurate,
                :year, :round, :source, :ingested_at
            )
            ON CONFLICT (race_key, driver_code, lap_number)
            DO UPDATE SET
                lap_seconds = EXCLUDED.lap_seconds,
                compound    = EXCLUDED.compound,
                tyre_life   = EXCLUDED.tyre_life,
                is_accurate = EXCLUDED.is_accurate,
                ingested_at = EXCLUDED.ingested_at
        """)
 
        return self._execute_batch(df, stmt, "telemetry_raw")
 
    def insert_validation_failure(
        self,
        table: str,
        race_key: str,
        failure_reason: str,
        raw_data: dict | None = None,
    ) -> None:
        """
        Append a validation failure to the audit log.
        Never raises — audit logging must not crash the pipeline.
        """
        try:
            with get_session() as session:
                session.execute(text("""
                    INSERT INTO validation_failures
                        (source_table, race_key, failure_reason, raw_data, occurred_at)
                    VALUES
                        (:source_table, :race_key, :failure_reason, :raw_data, :occurred_at)
                """), {
                    "source_table": table,
                    "race_key": race_key,
                    "failure_reason": failure_reason,
                    "raw_data": raw_data,
                    "occurred_at": datetime.now(timezone.utc),
                })
        except Exception as e:
            # Swallowed intentionally — this is audit logging, not critical path
            logger.error(f"validation_failures insert failed: {e}")


    # ------------------------------------------------------------------
    # Internal
    # ------------------------------------------------------------------
 
    def _execute_batch(
        self,
        df: pd.DataFrame,
        stmt,
        table: str,
        defaults: dict[str, object] | None = None,
    ) -> int:
        """
        Execute a parameterised statement in batches of _BATCH_SIZE.
        Raises StorageError on any batch failure.
        """
        rows = self._prepare_rows(df, defaults=defaults)
        total = 0
        num_batches = (len(rows) + _BATCH_SIZE - 1) // _BATCH_SIZE
 
        try:
            with get_session() as session:
                for i in range(num_batches):
                    batch = rows[i * _BATCH_SIZE:(i + 1) * _BATCH_SIZE]
                    session.execute(stmt, batch)
                    total += len(batch)
                    logger.info(
                        f"Batch {i+1}/{num_batches} → {len(batch)} rows into {table}"
                    )
        except StorageError:
            raise
        except Exception as e:
            raise StorageError(table, str(e)) from e
 
        logger.info(f"Total upserted: {total} rows into {table}")
        return total
 
    @staticmethod
    def _prepare_rows(
        df: pd.DataFrame,
        defaults: dict[str, object] | None = None,
    ) -> list[dict]:
        """
        Convert DataFrame to plain Python dicts.
        Adds ingested_at timestamp.
        Casts numpy types to Python native — SQLAlchemy's driver
        cannot serialise numpy.int64 / numpy.float64.
        """
        now = datetime.now(timezone.utc)
        rows = df.to_dict(orient="records")
        cleaned = []
 
        for row in rows:
            row["ingested_at"] = now
            clean_row = {k: _to_python_type(v) for k, v in row.items()}

            if defaults:
                for key, default_value in defaults.items():
                    clean_row.setdefault(key, default_value)

            cleaned.append(clean_row)
 
        return cleaned
