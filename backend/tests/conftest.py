# tests/conftest.py — remove the sqlite override completely
import pandas as pd
import pytest
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker
from app.db.base import Base
import app.db.models  # noqa

@pytest.fixture(scope="session")
def engine():
    from app.core.config import config
    _engine = create_engine(config.DATABASE_URL)
    Base.metadata.create_all(bind=_engine)
    yield _engine
    _engine.dispose()

@pytest.fixture(scope="function")
def session(engine):
    connection = engine.connect()
    transaction = connection.begin()
    Session = sessionmaker(bind=connection)
    db = Session()
    yield db
    db.close()
    transaction.rollback()  # rolls back after every test — no dirty data
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

@pytest.fixture
def results_df():
    return pd.DataFrame([
        {
            "driver_code": "VER", "driver_id": "max_verstappen",
            "driver_name": "Max Verstappen", "team": "Red Bull Racing",
            "team_id": "red_bull", "grid_position": 1, "finish_position": 1,
            "points": 25.0, "status": "Finished", "year": 2024, "round": 1,
            "race_key": "bahrain_grand_prix_2024", "race_name": "Bahrain Grand Prix",
            "circuit_id": "bahrain", "source": "ergast",
        },
        {
            "driver_code": "LEC", "driver_id": "leclerc",
            "driver_name": "Charles Leclerc", "team": "Ferrari",
            "team_id": "ferrari", "grid_position": 2, "finish_position": 2,
            "points": 18.0, "status": "Finished", "year": 2024, "round": 1,
            "race_key": "bahrain_grand_prix_2024", "race_name": "Bahrain Grand Prix",
            "circuit_id": "bahrain", "source": "ergast",
        },
    ])
 
 
@pytest.fixture
def telemetry_df():
    return pd.DataFrame([
        {
            "driver_code": "VER", "lap_number": 1, "lap_seconds": 95.2,
            "stint": 1, "compound": "SOFT", "tyre_life": 1, "is_accurate": True,
            "year": 2024, "round": 1, "race_key": "bahrain_grand_prix_2024", "source": "fastf1",
        },
        {
            "driver_code": "VER", "lap_number": 2, "lap_seconds": 90.1,
            "stint": 1, "compound": "SOFT", "tyre_life": 2, "is_accurate": True,
            "year": 2024, "round": 1, "race_key": "bahrain_grand_prix_2024", "source": "fastf1",
        },
        {
            "driver_code": "LEC", "lap_number": 1, "lap_seconds": 96.0,
            "stint": 1, "compound": "SOFT", "tyre_life": 1, "is_accurate": True,
            "year": 2024, "round": 1, "race_key": "bahrain_grand_prix_2024", "source": "fastf1",
        },
    ])