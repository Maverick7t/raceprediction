"""
conftest.py — shared fixtures for all Phase 1 tests.
 
Unit tests use SQLite in-memory (no network, no credentials needed).
Integration tests use real Postgres via DATABASE_URL env var.
"""
 
import os
import pytest
import pandas as pd
 
from sqlalchemy import create_engine, event
from sqlalchemy.orm import sessionmaker
 
os.environ.setdefault("DATABASE_URL", "sqlite:///:memory:")
os.environ.setdefault("ENVIRONMENT", "test")
os.environ.setdefault("LOG_LEVEL", "WARNING")
 
from app.db.base import Base
import app.db.models  # noqa — registers all models on Base.metadata
 
 
@pytest.fixture(scope="session")
def engine():
    _engine = create_engine(
        "sqlite:///:memory:",
        connect_args={"check_same_thread": False},
    )
 
    @event.listens_for(_engine, "connect")
    def set_pragma(dbapi_conn, _):
        dbapi_conn.cursor().execute("PRAGMA foreign_keys=ON")
 
    Base.metadata.create_all(bind=_engine)
    yield _engine
    _engine.dispose()
 
 @pytest.fixture(scope="function")
def session(engine):
    connection = engine.connect()
    transaction = connection.begin()
    Session = sessionmaker(bind=connection, autoflush=False, autocommit=False)
    db = Session()
    yield db
    db.close()
    transaction.rollback()
    connection.close()
 
 
@pytest.fixture
def qualifying_df():
    return pd.DataFrame([
        {
            "driver_code": "VER", "driver_id": "max_verstappen",
            "driver_name": "Max Verstappen", "team": "Red Bull Racing",
            "team_id": "red_bull", "position": 1,
            "q1_time": "1:28.123", "q2_time": "1:27.456", "q3_time": "1:26.720",
            "best_lap_seconds": 86.72, "year": 2024, "round": 1,
            "race_key": "bahrain_grand_prix_2024", "race_name": "Bahrain Grand Prix",
            "circuit_id": "bahrain", "source": "ergast",
        },
        {
            "driver_code": "LEC", "driver_id": "leclerc",
            "driver_name": "Charles Leclerc", "team": "Ferrari",
            "team_id": "ferrari", "position": 2,
            "q1_time": "1:28.200", "q2_time": "1:27.600", "q3_time": "1:26.850",
            "best_lap_seconds": 86.85, "year": 2024, "round": 1,
            "race_key": "bahrain_grand_prix_2024", "race_name": "Bahrain Grand Prix",
            "circuit_id": "bahrain", "source": "ergast",
        },
    ])