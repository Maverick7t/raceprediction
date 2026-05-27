from datetime import datetime
from sqlalchemy import BigInteger, Float, Index, SmallInteger, Text, TIMESTAMP, UniqueConstraint, func
from sqlalchemy.orm import Mapped, mapped_column
from app.db.base import Base


class Prediction(Base):
    __tablename__ = "predictions"

    id: Mapped[int] = mapped_column(BigInteger, primary_key=True)
    race_key: Mapped[str] = mapped_column(Text, nullable=False)
    driver_code: Mapped[str] = mapped_column(Text, nullable=False)
    driver_name: Mapped[str] = mapped_column(Text, nullable=False)
    team_id: Mapped[str] = mapped_column(Text, nullable=False)
    qualifying_position: Mapped[int | None] = mapped_column(SmallInteger)
    predicted_winner_prob: Mapped[float] = mapped_column(Float, nullable=False)
    predicted_podium_prob: Mapped[float] = mapped_column(Float, nullable=False)
    predicted_rank: Mapped[int] = mapped_column(SmallInteger, nullable=False)
    model_version: Mapped[str] = mapped_column(Text, nullable=False)
    feature_version: Mapped[str] = mapped_column(Text, nullable=False)
    generated_at: Mapped[datetime] = mapped_column(
        TIMESTAMP(timezone=True), nullable=False, server_default=func.now()
    )

    __table_args__ = (
        UniqueConstraint("race_key", "driver_code", name="predictions_race_driver_unique"),
        Index("idx_predictions_race_key", "race_key"),
        Index("idx_predictions_generated_at", "generated_at"),
    )