from datetime import datetime
from sqlalchemy import (
    Binginteger,
    CheckConstraint,
    Float,
    Index,
    SmallInteger,
    Text,
    TIMESTAMP,
    UniqueConstraint,
    func,
)

from sqlalchemy.orm import (
    Mapped,
    mapped_column,

)

from app.db.base import Base

class ResultRaw(Base):
    __tablename__ = "results_raw"

    id: Mapped[int] = mapped_column(
        Binginteger, 
        primary_key=True,
    )

    race_key: Mapped[str] = mapped_column(
        Text,
        nullable=False,
    )

    driver_code: Mapped[str] = mapped_column(
        Text,
        nullable=False,
    )

    driver_id: Mapped[str] = mapped_column(
        Text,
        nullable=False,
    )

    driver_name: Mapped[str] = mapped_column(
        Text,
        nullable=False,
    )

    team: Mapped[str] = mapped_column(
        Text,
        nullable=False,
    )

    team_id: Mapped[str] = mapped_column(
        Text,
        nullable=False,
    )

    grid_position: Mapped[int] = mapped_column(
        SmallInteger,
        nullable=False,
    )

    finish_position: Mapped[int] = mapped_column(
        SmallInteger,
        nullable=False,
    )

    points: Mapped[float] = mapped_column(
        Float,
        nullable=False,
    )

    status: Mapped[str] = mapped_column(
        Text,
        nullable=False,
    )

    year: Mapped[int] = mapped_column(
        SmallInteger,
        nullable=False,
    )

    round: Mapped[int] = mapped_column(
        SmallInteger,
        nullable=False,
    )   

    race_name: Mapped[str] = mapped_column(
        Text,
        nullable=False,
    )

    circuit_id: Mapped[str] = mapped_column(
        Text,
         nullable=False,
    )

    source: Mapped[str] = mapped_column(
        Text,
         nullable=False,
    )

    ingested_at: Mapped[datetime] = mapped_column(
        TIMESTAMP(timezone=True),
        nullable=False,
        server_default=func.now(),
    )

    __table_args__ = (
        UniqueConstraint(
            "race_key",
            "driver_code",
            name="race_driver_unique",
        ),

        CheckConstraint(
            "grid_position BETWEEN 0 AND 20",
            name="grid_position_range",
        ),

        CheckConstraint(
            "finish_position BETWEEN 1 AND 20",
            name="finish_position_range",
        ),

        CheckConstraint(
            "points >= 0",
            name="points_non_negative",
        ),

        Index(
            "idx_results_race_key",
            "race_key",
        ),

        Index(
            "idx_results_driver_year",
            "driver_code",
            "year",
        ),
    )