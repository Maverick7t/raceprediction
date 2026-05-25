"""
features_by_race table.
 
One row per driver per race. Stores all precomputed features.
This is what the ML model reads — never the raw tables directly.
 
feature_version column:
  Bump from 'v1' to 'v2' when you add/rename/change any feature column.
  Training pipeline always reads one specific version.
  Inference always reads the same version the production model was trained on.
  NEVER mix versions in one training run.
 
Conflict key: (race_key, driver_code, feature_version)
  Safe to rerun the feature pipeline multiple times.
"""
 
from __future__ import annotations
from datetime import datetime
 
from sqlalchemy import (
    BigInteger, Float, Index, SmallInteger,
    Text, TIMESTAMP, UniqueConstraint, func,
)
from sqlalchemy.orm import Mapped, mapped_column
 
from app.db.base import Base
 
 
class FeaturesByRace(Base):
    __tablename__ = "features_by_race"
 
    id: Mapped[int] = mapped_column(BigInteger, primary_key=True)
 
    # --- Identity ---
    race_key: Mapped[str] = mapped_column(Text, nullable=False)
    driver_code: Mapped[str] = mapped_column(Text, nullable=False)
    driver_name: Mapped[str] = mapped_column(Text, nullable=False)
    team_id: Mapped[str] = mapped_column(Text, nullable=False)
    year: Mapped[int] = mapped_column(SmallInteger, nullable=False)
    round: Mapped[int] = mapped_column(SmallInteger, nullable=False)
    circuit_id: Mapped[str] = mapped_column(Text, nullable=False)
    feature_version: Mapped[str] = mapped_column(Text, nullable=False, default="v1")

    # --- Driver features ---
    avg_finish_last_5: Mapped[float | None] = mapped_column(Float)
    avg_quali_last_5: Mapped[float | None] = mapped_column(Float)
    podium_rate: Mapped[float | None] = mapped_column(Float)
    dnf_rate: Mapped[float | None] = mapped_column(Float)
    wet_weather_score: Mapped[float | None] = mapped_column(Float)
    teammate_delta: Mapped[float | None] = mapped_column(Float)
    tire_management_score: Mapped[float | None] = mapped_column(Float)
 
    # --- Team features ---
    constructor_form: Mapped[float | None] = mapped_column(Float)
    pitstop_avg: Mapped[float | None] = mapped_column(Float)
    reliability_score: Mapped[float | None] = mapped_column(Float)

    # --- Circuit features ---
    overtaking_difficulty: Mapped[float | None] = mapped_column(Float)
    tire_deg_factor: Mapped[float | None] = mapped_column(Float)
    safety_car_probability: Mapped[float | None] = mapped_column(Float)
 
    # --- Session features (available after qualifying) ---
    qualifying_position: Mapped[int | None] = mapped_column(SmallInteger)
    qualifying_delta_to_pole: Mapped[float | None] = mapped_column(Float)
 
    # --- Target (filled after race, used for training) ---
    finish_position: Mapped[int | None] = mapped_column(SmallInteger)
    is_winner: Mapped[int | None] = mapped_column(SmallInteger)   # 1 or 0
    is_podium: Mapped[int | None] = mapped_column(SmallInteger)   # 1 or 0
 
    computed_at: Mapped[datetime] = mapped_column(
        TIMESTAMP(timezone=True), nullable=False, server_default=func.now()
    )
 
    __table_args__ = (
        UniqueConstraint(
            "race_key", "driver_code", "feature_version",
            name="features_race_driver_version_unique",
        ),
        Index("idx_features_race_key", "race_key"),
        Index("idx_features_driver_year", "driver_code", "year"),
        Index("idx_features_version", "feature_version"),
    )
 
    def __repr__(self) -> str:
        return f"<FeaturesByRace {self.race_key} {self.driver_code} {self.feature_version}>"