from datetime import date, datetime

from sqlalchemy import (
    BigInteger,
    CheckConstraint,
    Date,
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


class ResultsRaw(Base):
    __tablename__ = "results_raw"

    id: Mapped[int] = mapped_column(
        BigInteger,
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

    race_date: Mapped[date | None] = mapped_column(
        Date,
        nullable=True,
    )

    __table_args__ = (
        UniqueConstraint(
            "race_key",
            "driver_code",
        ),

        CheckConstraint(grid_position.between(0, 20)),

        CheckConstraint(finish_position.between(1, 20)),

        CheckConstraint(points >= 0),

        Index(
            None,
            "race_key",
        ),

        Index(
            None,
            "driver_code",
            "year",
        ),
    )