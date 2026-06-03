from datetime import datetime

from sqlalchemy import (
    BigInteger,
    Boolean,
    CheckConstraint,
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


class TelemetryRaw(Base):
    __tablename__ = "telemetry_raw"

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

    lap_number: Mapped[int] = mapped_column(
        SmallInteger,
        nullable=False,
    )

    lap_seconds: Mapped[float | None]

    stint: Mapped[int] = mapped_column(
        SmallInteger,
        nullable=False,
    )

    # intentionally relaxed
    # validate upstream values in Pandera
    compound: Mapped[str | None]

    tyre_life: Mapped[int | None]

    is_accurate: Mapped[bool | None] = mapped_column(
        Boolean,
    )

    year: Mapped[int] = mapped_column(
        SmallInteger,
        nullable=False,
    )

    round: Mapped[int] = mapped_column(
        SmallInteger,
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
            "lap_number",
        ),

        CheckConstraint(lap_number > 0),

        CheckConstraint(stint > 0),

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