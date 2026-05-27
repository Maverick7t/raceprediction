"""
PredictionRepository

Writes predictions after inference (Prefect flow).
Reads predictions for API serving.
All writes are upserts — idempotent, safe to re-run.
"""

from datetime import datetime, timezone

import pandas as pd
from sqlalchemy import text

from app.core.exceptions import StorageError
from app.core.logging import get_logger
from app.db.session import get_session

logger = get_logger(__name__)


class PredictionRepository:

    def upsert_predictions(self, df: pd.DataFrame) -> int:
        """
        Upsert prediction rows.
        Conflict key: (race_key, driver_code).
        Called by inference_tasks after qualifying.
        """
        if df is None or df.empty:
            logger.warning("upsert_predictions called with empty DataFrame")
            return 0

        stmt = text("""
            INSERT INTO predictions (
                race_key, driver_code, driver_name, team_id,
                qualifying_position, predicted_winner_prob, predicted_podium_prob,
                predicted_rank, model_version, feature_version, generated_at
            ) VALUES (
                :race_key, :driver_code, :driver_name, :team_id,
                :qualifying_position, :predicted_winner_prob, :predicted_podium_prob,
                :predicted_rank, :model_version, :feature_version, :generated_at
            )
            ON CONFLICT (race_key, driver_code)
            DO UPDATE SET
                predicted_winner_prob = EXCLUDED.predicted_winner_prob,
                predicted_podium_prob = EXCLUDED.predicted_podium_prob,
                predicted_rank        = EXCLUDED.predicted_rank,
                qualifying_position   = EXCLUDED.qualifying_position,
                model_version         = EXCLUDED.model_version,
                feature_version       = EXCLUDED.feature_version,
                generated_at          = EXCLUDED.generated_at
        """)

        rows = self._prepare_rows(df)
        try:
            with get_session() as session:
                session.execute(stmt, rows)
            logger.info(f"Upserted {len(rows)} prediction rows")
            return len(rows)
        except Exception as e:
            raise StorageError("predictions", str(e)) from e
        
    def get_predictions_for_race(self, race_key: str) -> pd.DataFrame:
        """Read all predictions for a specific race, ranked order."""
        with get_session() as session:
            result = session.execute(text("""
                SELECT race_key, driver_code, driver_name, team_id,
                       qualifying_position, predicted_winner_prob,
                       predicted_podium_prob, predicted_rank,
                       model_version, feature_version, generated_at
                FROM predictions
                WHERE race_key = :race_key
                ORDER BY predicted_rank ASC
            """), {"race_key": race_key})
            rows = result.mappings().all()

        if not rows:
            logger.warning(f"No predictions found for race_key={race_key}")
        return pd.DataFrame(rows)