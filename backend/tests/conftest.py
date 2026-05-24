"""
Shared pytest fixtures for Phase 1 tests.
 
All external dependencies (Supabase, FastF1, Ergast) are mocked at the
boundary — unit tests never make real network calls.
"""
 
import pandas as pd
import pytest
 
 
# ---------------------------------------------------------------------------
# Sample DataFrames — used across multiple test files
# ---------------------------------------------------------------------------
 
@pytest.fixture
def valid_qualifying_df():
    """A minimal valid qualifying DataFrame that passes QualifyingRawSchema."""
    return pd.DataFrame([
        {
            "driver_code": "VER",
            "driver_id": "max_verstappen",
            "driver_name": "Max Verstappen",
            "team": "Red Bull Racing",
            "team_id": "red_bull",
            "position": 1,
            "q1_time": "1:28.123",
            "q2_time": "1:27.456",
            "q3_time": "1:26.720",
            "best_lap_seconds": 86.72,
            "year": 2024,
            "round": 1,
            "race_key": "bahrain_grand_prix_2024",
            "race_name": "Bahrain Grand Prix",
            "circuit_id": "bahrain",
            "source": "ergast",
        },
        {
            "driver_code": "LEC",
            "driver_id": "leclerc",
            "driver_name": "Charles Leclerc",
            "team": "Ferrari",
            "team_id": "ferrari",
            "position": 2,
            "q1_time": "1:28.200",
            "q2_time": "1:27.600",
            "q3_time": "1:26.850",
            "best_lap_seconds": 86.85,
            "year": 2024,
            "round": 1,
            "race_key": "bahrain_grand_prix_2024",
            "race_name": "Bahrain Grand Prix",
            "circuit_id": "bahrain",
            "source": "ergast",
        },
    ])
 