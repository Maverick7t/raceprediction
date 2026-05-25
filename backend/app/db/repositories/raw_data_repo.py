"""
RawDataRepository
 
Handles all writes to the four raw-zone tables:
  qualifying_raw       — one row per driver per qualifying session
  results_raw          — one row per driver per race
  telemetry_raw        — one row per driver per lap
  validation_failures  — audit log of rows that failed Pandera validation
 
All writes are UPSERT. Conflict keys:
  qualifying_raw   → UNIQUE(race_key, driver_code)
  results_raw      → UNIQUE(race_key, driver_code)
  telemetry_raw    → UNIQUE(race_key, driver_code, lap_number)
  validation_failures → no unique constraint; append-only audit log
 
UPSERT means every pipeline run is idempotent —
re-running after a failure never creates duplicate rows.
"""
 
import math
from datetime import datetime, timezone
from typing import Optional
 
import numpy as np
import pandas as pd
 
from app.core.exceptions import StorageError
from app.core.logging import get_logger
from app.repositories.base import SupabaseRepository
 
logger = get_logger(__name__)
 
# Supabase has a per-request row limit. Batch large inserts to stay safe.
_BATCH_SIZE = 500
 
 
class RawDataRepository(SupabaseRepository):
 
    # ------------Public upsert methods-----------------------------------------

    def upsert_qualifying_raw(self, df: pd.DataFrame) -> int:
        """
        Upsert qualifying rows.
        Conflict key: (race_key, driver_code).
        Returns the number of rows written.
        """
        return self._upsert(df, "qualifying_raw", on_conflict="race_key,driver_code")
    
    def upsert_results_raw(self, df: pd.DataFrame) -> int:
        """
        Upsert race result rows.
        Conflict key: (race_key, driver_code).
        """
        return self._upsert(df, "results_raw", on_conflict="race_key,driver_code")
 
    def upsert_telemetry_raw(self, df: pd.DataFrame) -> int:
        """
        Upsert lap telemetry rows.
        Conflict key: (race_key, driver_code, lap_number).
        Telemetry tables can be large (1,000+ rows per race).
        Writes are batched to avoid hitting Supabase payload limits.
        """
        return self._upsert(
            df,
            "telemetry_raw",
            on_conflict="race_key,driver_code,lap_number",
        )
 
    def insert_validation_failure(
        self,
        table: str,
        race_key: str,
        failure_reason: str,
        raw_data: Optional[dict] = None,
    ) -> None:
        """
        Append a validation failure record to the audit log.
        This method never raises — validation logging must not crash the pipeline.
        If the insert itself fails, the error is logged and swallowed.
        """
        try:
            self.client.table("validation_failures").insert({
                "source_table": table,
                "race_key": race_key,
                "failure_reason": failure_reason,
                "raw_data": raw_data,
                "occurred_at": datetime.now(timezone.utc).isoformat(),
            }).execute()
        except Exception as e:
            # Swallowing intentionally — this is audit logging, not critical path
            logger.error(f"validation_failures insert failed: {e}")



    # ------------------------------------------------------------------
    # Internal
    # ------------------------------------------------------------------
 
    def _upsert(self, df: pd.DataFrame, table: str, on_conflict: str) -> int:
        if df is None or df.empty:
            logger.warning(f"_upsert called with empty DataFrame for table={table}")
            return 0
 
        rows = self._prepare_rows(df)
        total = 0
        num_batches = math.ceil(len(rows) / _BATCH_SIZE)
 
        for i in range(num_batches):
            batch = rows[i * _BATCH_SIZE : (i + 1) * _BATCH_SIZE]
            try:
                self.client.table(table).upsert(
                    batch, on_conflict=on_conflict
                ).execute()
                total += len(batch)
                logger.info(
                    f"Upserted batch {i+1}/{num_batches} "
                    f"({len(batch)} rows) into {table}"
                )
            except Exception as e:
                raise StorageError(table, f"Batch {i+1} upsert failed: {e}") from e
 
        logger.info(f"Upserted {total} total rows into {table}")
        return total
 
    @staticmethod
    def _prepare_rows(df: pd.DataFrame) -> list[dict]:
        """
        Convert DataFrame to a list of plain Python dicts.
        Supabase's JSON serialiser cannot handle numpy scalars (int64, float64),
        NaT, or pandas NA — all must be cast to Python native types or None.
        """
        rows = df.to_dict(orient="records")
        cleaned = []
        for row in rows:
            row["ingested_at"] = datetime.now(timezone.utc).isoformat()
            cleaned.append({k: _to_python_type(v) for k, v in row.items()})
        return cleaned