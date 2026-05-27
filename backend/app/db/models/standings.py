from datetime import datetime
from sqlalchemy import BigInteger, Float, Index, Integer, SmallInteger, Text, TIMESTAMP, UniqueConstraint, func
from sqlalchemy.orm import Mapped, mapped_column
from app.db.base import Base


class DriverStandings(Base):
    __tablename__ = "driver_standings_cache"

    id: Mapped[int] = mapped_column(BigInteger, primary_key=True)
    year: Mapped[int] = mapped_column(SmallInteger, nullable=False)
    round: Mapped[int | None] = mapped_column(SmallInteger)
    driver_code: Mapped[str] = mapped_column(Text, nullable=False)
    driver_id: Mapped[str] = mapped_column(Text, nullable=False)
    driver_name: Mapped[str] = mapped_column(Text, nullable=False)
    team: Mapped[str] = mapped_column(Text, nullable=False)
    position: Mapped[int] = mapped_column(SmallInteger, nullable=False)
    points: Mapped[float] = mapped_column(Float, nullable=False)
    wins: Mapped[int] = mapped_column(Integer, nullable=False)
    synced_at: Mapped[datetime] = mapped_column(
        TIMESTAMP(timezone=True), nullable=False, server_default=func.now()
    )

    __table_args__ = (
        UniqueConstraint("year", "driver_code", name="driver_standings_year_driver_unique"),
        Index("idx_driver_standings_year", "year"),
    )


    class ConstructorStandings(Base):
    __tablename__ = "constructor_standings_cache"

    id: Mapped[int] = mapped_column(BigInteger, primary_key=True)
    year: Mapped[int] = mapped_column(SmallInteger, nullable=False)
    round: Mapped[int | None] = mapped_column(SmallInteger)
    team_id: Mapped[str] = mapped_column(Text, nullable=False)
    team: Mapped[str] = mapped_column(Text, nullable=False)
    position: Mapped[int] = mapped_column(SmallInteger, nullable=False)
    points: Mapped[float] = mapped_column(Float, nullable=False)
    wins: Mapped[int] = mapped_column(Integer, nullable=False)
    synced_at: Mapped[datetime] = mapped_column(
        TIMESTAMP(timezone=True), nullable=False, server_default=func.now()
    )

    __table_args__ = (
        UniqueConstraint("year", "team_id", name="constructor_standings_year_team_unique"),
        Index("idx_constructor_standings_year", "year"),
    )
