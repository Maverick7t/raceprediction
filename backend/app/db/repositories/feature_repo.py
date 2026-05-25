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