from datetime import datetime

from sqlalchemy import (
    BigInteger,
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


class QualifyingRaw(Base):
    __tablename__ = "qualifying_raw"

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

    position: Mapped[int] = mapped_column(
        SmallInteger,
        nullable=False,
    )

    q1_time: Mapped[str | None]
    q2_time: Mapped[str | None]
    q3_time: Mapped[str | None]

    best_lap_seconds: Mapped[float | None]

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

    race_date: Mapped[datetime | None] = mapped_column(
        Date,
        nullable=True,
    )

    __table_args__ = (
        UniqueConstraint(
            "race_key",
            "driver_code",
        ),

        CheckConstraint(position.between(1, 20)),

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