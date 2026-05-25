"""
FeatureRepository
 
All reads and writes to features_by_race table.
The ML training pipeline reads from here.
The inference engine reads from here.
Nothing else writes to this table directly.
"""
 
from datetime import datetime, timezone
 
import pandas as pd
from sqlalchemy import text
 
from app.core.exceptions import StorageError
from app.core.logging import get_logger
from app.db.session import get_session
 
logger = get_logger(__name__)
 
CURRENT_FEATURE_VERSION = "v1"
 
 
class FeatureRepository:
 
    def upsert_features(self, df: pd.DataFrame) -> int:
        """
        Upsert feature rows.
        Conflict key: (race_key, driver_code, feature_version).
        """
        if df is None or df.empty:
            logger.warning("upsert_features called with empty DataFrame")
            return 0
 
        rows = self._prepare_rows(df)
 
        stmt = text("""
            INSERT INTO features_by_race (
                race_key, driver_code, driver_name, team_id,
                year, round, circuit_id, feature_version,
                avg_finish_last_5, avg_quali_last_5, podium_rate, dnf_rate,
                wet_weather_score, teammate_delta, tire_management_score,
                constructor_form, pitstop_avg, reliability_score,
                overtaking_difficulty, tire_deg_factor, safety_car_probability,
                qualifying_position, qualifying_delta_to_pole,
                finish_position, is_winner, is_podium, computed_at
            ) VALUES (
                :race_key, :driver_code, :driver_name, :team_id,
                :year, :round, :circuit_id, :feature_version,
                :avg_finish_last_5, :avg_quali_last_5, :podium_rate, :dnf_rate,
                :wet_weather_score, :teammate_delta, :tire_management_score,
                :constructor_form, :pitstop_avg, :reliability_score,
                :overtaking_difficulty, :tire_deg_factor, :safety_car_probability,
                :qualifying_position, :qualifying_delta_to_pole,
                :finish_position, :is_winner, :is_podium, :computed_at
            )
            ON CONFLICT (race_key, driver_code, feature_version)
            DO UPDATE SET
                avg_finish_last_5        = EXCLUDED.avg_finish_last_5,
                avg_quali_last_5         = EXCLUDED.avg_quali_last_5,
                podium_rate              = EXCLUDED.podium_rate,
                dnf_rate                 = EXCLUDED.dnf_rate,
                wet_weather_score        = EXCLUDED.wet_weather_score,
                teammate_delta           = EXCLUDED.teammate_delta,
                tire_management_score    = EXCLUDED.tire_management_score,
                constructor_form         = EXCLUDED.constructor_form,
                pitstop_avg              = EXCLUDED.pitstop_avg,
                reliability_score        = EXCLUDED.reliability_score,
                qualifying_position      = EXCLUDED.qualifying_position,
                qualifying_delta_to_pole = EXCLUDED.qualifying_delta_to_pole,
                finish_position          = EXCLUDED.finish_position,
                is_winner                = EXCLUDED.is_winner,
                is_podium                = EXCLUDED.is_podium,
                computed_at              = EXCLUDED.computed_at
        """)


        try:
            with get_session() as session:
                session.execute(stmt, rows)
            logger.info(f"Upserted {len(rows)} feature rows")
            return len(rows)
        except Exception as e:
            raise StorageError("features_by_race", str(e)) from e
 
    def get_features_for_race(
        self, race_key: str, feature_version: str = CURRENT_FEATURE_VERSION
    ) -> pd.DataFrame:
        """
        Read all feature rows for a specific race.
        Used by the inference engine after qualifying.
        """
        with get_session() as session:
            result = session.execute(text("""
                SELECT * FROM features_by_race
                WHERE race_key = :race_key
                AND feature_version = :feature_version
                ORDER BY qualifying_position ASC NULLS LAST
            """), {"race_key": race_key, "feature_version": feature_version})
            rows = result.mappings().all()
 
        if not rows:
            logger.warning(f"No features found for race_key={race_key} version={feature_version}")
            return pd.DataFrame()
 
        return pd.DataFrame(rows)
    

    def get_training_dataset(
        self,
        feature_version: str = CURRENT_FEATURE_VERSION,
        from_year: int = 2018,
    ) -> pd.DataFrame:
        """
        Read all feature rows that have a known result (finish_position not null).
        Used by the ML training pipeline.
        Only returns rows where is_winner and is_podium targets are populated.
        """
        with get_session() as session:
            result = session.execute(text("""
                SELECT * FROM features_by_race
                WHERE feature_version = :feature_version
                AND year >= :from_year
                AND finish_position IS NOT NULL
                AND is_winner IS NOT NULL
                AND is_podium IS NOT NULL
                ORDER BY year ASC, round ASC
            """), {"feature_version": feature_version, "from_year": from_year})
            rows = result.mappings().all()
 
        df = pd.DataFrame(rows)
        logger.info(
            f"Training dataset: {len(df)} rows "
            f"version={feature_version} from_year={from_year}"
        )
        return df
    
    def count_rows_for_version(self, feature_version: str = CURRENT_FEATURE_VERSION) -> int:
        with get_session() as session:
            count = session.execute(text("""
                SELECT COUNT(*) FROM features_by_race
                WHERE feature_version = :version
            """), {"version": feature_version}).scalar()
        return count or 0
 
    @staticmethod
    def _prepare_rows(df: pd.DataFrame) -> list[dict]:
        import math
        import numpy as np
 
        now = datetime.now(timezone.utc)
        rows = df.to_dict(orient="records")
        cleaned = []
 
        for row in rows:
            row.setdefault("computed_at", now)
            row.setdefault("feature_version", CURRENT_FEATURE_VERSION)
            clean = {}
            for k, v in row.items():
                if v is None:
                    clean[k] = None
                elif isinstance(v, np.integer):
                    clean[k] = int(v)
                elif isinstance(v, np.floating):
                    clean[k] = None if math.isnan(v) else float(v)
                elif isinstance(v, np.bool_):
                    clean[k] = bool(v)
                elif isinstance(v, float) and math.isnan(v):
                    clean[k] = None
                else:
                    try:
                        clean[k] = None if pd.isna(v) else v
                    except (TypeError, ValueError):
                        clean[k] = v
            cleaned.append(clean)
 
        return cleaned