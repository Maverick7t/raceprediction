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
    
    def get_latest_predictions(self) -> pd.DataFrame:
        """Return predictions for the most recently generated race."""
        with get_session() as session:
            result = session.execute(text("""
                SELECT p.race_key, p.driver_code, p.driver_name, p.team_id,
                       p.qualifying_position, p.predicted_winner_prob,
                       p.predicted_podium_prob, p.predicted_rank,
                       p.model_version, p.feature_version, p.generated_at
                FROM predictions p
                INNER JOIN (
                    SELECT race_key
                    FROM predictions
                    ORDER BY generated_at DESC
                    LIMIT 1
                ) latest ON p.race_key = latest.race_key
                ORDER BY p.predicted_rank ASC
            """))
            rows = result.mappings().all()
        return pd.DataFrame(rows)

    def list_race_keys(self) -> list[str]:
        """All race keys that have stored predictions, newest first."""
        with get_session() as session:
            result = session.execute(text("""
                SELECT DISTINCT race_key
                FROM predictions
                ORDER BY race_key DESC
            """))
            return [r[0] for r in result.fetchall()]

    def get_most_recent_generated_at(self) -> datetime | None:
        """Used by the staleness health check."""
        with get_session() as session:
            result = session.execute(text("""
                SELECT MAX(generated_at) FROM predictions
            """))
            value = result.scalar()
        return value
