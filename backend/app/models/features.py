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