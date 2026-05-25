"""
Unit tests — Phase 2 feature computation.
 
WHEN TO RUN:
  After writing/changing any function in app/features/compute.py
    pytest tests/unit/test_features.py -v
  CI: runs on every push.
 
No database calls. All computation functions are pure — they take
DataFrames and return values. Database loading is mocked.
"""
 
import pandas as pd
import numpy as np
import pytest
 
from app.features.compute import (
    _avg_finish,
    _avg_quali,
    _podium_rate,
    _dnf_rate,
    _teammate_delta,
    _tire_management_score,
    _constructor_form,
    _reliability_score,
    DNF_STATUSES,
    WINDOW,
)

---------------------------------------------------------------------------
# Fixtures
# ---------------------------------------------------------------------------
 
@pytest.fixture
def driver_results_5():
    """5 races of clean results — P1, P2, P3, P4, P5."""
    return pd.DataFrame([
        {"driver_code": "VER", "team_id": "red_bull", "finish_position": 1, "points": 25.0, "status": "Finished", "year": 2024, "round": i}
        for i in range(1, 6)
    ])
 
 
@pytest.fixture
def driver_results_with_dnf():
    """5 races — 2 DNFs."""
    rows = [
        {"driver_code": "VER", "team_id": "red_bull", "finish_position": 1, "points": 25.0, "status": "Finished", "year": 2024, "round": 1},
        {"driver_code": "VER", "team_id": "red_bull", "finish_position": 1, "points": 0.0, "status": "Engine", "year": 2024, "round": 2},
        {"driver_code": "VER", "team_id": "red_bull", "finish_position": 2, "points": 18.0, "status": "Finished", "year": 2024, "round": 3},
        {"driver_code": "VER", "team_id": "red_bull", "finish_position": 1, "points": 0.0, "status": "Collision", "year": 2024, "round": 4},
        {"driver_code": "VER", "team_id": "red_bull", "finish_position": 3, "points": 15.0, "status": "Finished", "year": 2024, "round": 5},
    ]
    return pd.DataFrame(rows)
 
 
@pytest.fixture
def quali_history():
    """Two drivers, same team, 3 rounds."""
    return pd.DataFrame([
        {"driver_code": "VER", "team_id": "red_bull", "position": 1, "best_lap_seconds": 86.5, "year": 2024, "round": 1},
        {"driver_code": "PER", "team_id": "red_bull", "position": 4, "best_lap_seconds": 87.1, "year": 2024, "round": 1},
        {"driver_code": "VER", "team_id": "red_bull", "position": 1, "best_lap_seconds": 85.9, "year": 2024, "round": 2},
        {"driver_code": "PER", "team_id": "red_bull", "position": 5, "best_lap_seconds": 86.8, "year": 2024, "round": 2},
        {"driver_code": "VER", "team_id": "red_bull", "position": 2, "best_lap_seconds": 87.1, "year": 2024, "round": 3},
        {"driver_code": "PER", "team_id": "red_bull", "position": 3, "best_lap_seconds": 87.3, "year": 2024, "round": 3},
    ])
 
 
@pytest.fixture
def telemetry_df():
    """20 laps of telemetry — 2 stints, accurate laps only."""
    rows = []
    for lap in range(1, 21):
        rows.append({
            "driver_code": "VER",
            "lap_number": lap,
            "lap_seconds": 90.0 + (lap * 0.05),  # mild degradation
            "stint": 1 if lap <= 10 else 2,
            "tyre_life": lap if lap <= 10 else lap - 10,
            "compound": "SOFT" if lap <= 10 else "MEDIUM",
            "is_accurate": True,
        })
    return pd.DataFrame(rows)


# ---------------------------------------------------------------------------
# avg_finish
# ---------------------------------------------------------------------------
 
class TestAvgFinish:
 
    def test_basic_average(self, driver_results_5):
        result = _avg_finish(driver_results_5)
        assert result == pytest.approx(3.0, abs=0.01)
 
    def test_empty_returns_none(self):
        assert _avg_finish(pd.DataFrame()) is None
 
    def test_dnf_excluded_from_average(self, driver_results_with_dnf):
        """DNFs don't count as a finish — excluded from avg calculation."""
        result = _avg_finish(driver_results_with_dnf)
        # Finished: P1, P2, P3 → avg = 2.0
        assert result == pytest.approx(2.0, abs=0.01)
 
    def test_uses_only_last_5(self):
        """Only the most recent WINDOW races are used."""
        rows = [
            {"driver_code": "VER", "team_id": "red_bull", "finish_position": 20,
             "points": 0.0, "status": "Finished", "year": 2023, "round": i}
            for i in range(1, 11)   # 10 old races at P20
        ] + [
            {"driver_code": "VER", "team_id": "red_bull", "finish_position": 1,
             "points": 25.0, "status": "Finished", "year": 2024, "round": i}
            for i in range(1, 6)    # 5 recent races at P1
        ]
        df = pd.DataFrame(rows)
        result = _avg_finish(df)
        assert result == pytest.approx(1.0, abs=0.01)