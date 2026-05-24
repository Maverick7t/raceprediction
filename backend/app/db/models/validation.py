from datetime import datetime

from sqlalchemy import (
    BigInteger,
    Index,
    Text,
    TIMESTAMP,
    func,
)

from sqlalchemy.dialects.postgresql import JSONB

from sqlalchemy.orm import (
    Mapped,
    mapped_column,
)

from app.db.base import Base


class ValidationFailure(Base):
    __tablename__ = "validation_failures"

    id: Mapped[int] = mapped_column(
        BigInteger,
        primary_key=True,
    )

    source_table: Mapped[str] = mapped_column(
        Text,
        nullable=False,
    )

    race_key: Mapped[str] = mapped_column(
        Text,
        nullable=False,
    )

    failure_reason: Mapped[str] = mapped_column(
        Text,
        nullable=False,
    )

    raw_data: Mapped[dict | None] = mapped_column(
        JSONB,
    )

    occurred_at: Mapped[datetime] = mapped_column(
        TIMESTAMP(timezone=True),
        nullable=False,
        server_default=func.now(),
    )

    __table_args__ = (
        Index(
            "idx_validation_race_key",
            "race_key",
        ),

        Index(
            "idx_validation_occurred_at",
            "occurred_at",
        ),
    )