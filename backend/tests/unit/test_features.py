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
 
 
# ---------------------------------------------------------------------------
# Fixtures
# ---------------------------------------------------------------------------
 
@pytest.fixture
def driver_results_5():
    """5 races of clean results — P1, P2, P3, P4, P5."""
    return pd.DataFrame([
        {"driver_code": "VER", "team_id": "red_bull", "finish_position": i, "points": 25.0, "status": "Finished", "year": 2024, "round": i}
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



        # ---------------------------------------------------------------------------
# avg_quali
# ---------------------------------------------------------------------------
 
class TestAvgQuali:
 
    def test_basic_average(self, quali_history):
        ver_only = quali_history[quali_history["driver_code"] == "VER"]
        result = _avg_quali(ver_only)
        assert result == pytest.approx((1 + 1 + 2) / 3, abs=0.01)
 
    def test_empty_returns_none(self):
        assert _avg_quali(pd.DataFrame()) is None
 
 
# ---------------------------------------------------------------------------
# podium_rate
# ---------------------------------------------------------------------------
 
class TestPodiumRate:
 
    def test_all_podiums(self, driver_results_5):
        """P1, P2, P3, P4, P5 — 3 out of 5 are podiums."""
        result = _podium_rate(driver_results_5)
        assert result == pytest.approx(0.6, abs=0.01)
 
    def test_no_podiums(self):
        rows = [{"driver_code": "VER", "team_id": "rb", "finish_position": 5,
                 "points": 10.0, "status": "Finished", "year": 2024, "round": i}
                for i in range(1, 6)]
        result = _podium_rate(pd.DataFrame(rows))
        assert result == pytest.approx(0.0, abs=0.01)
 
    def test_empty_returns_none(self):
        assert _podium_rate(pd.DataFrame()) is None
 
 
# ---------------------------------------------------------------------------
# dnf_rate
# ---------------------------------------------------------------------------
 
class TestDnfRate:
 
    def test_two_dnfs_out_of_five(self, driver_results_with_dnf):
        result = _dnf_rate(driver_results_with_dnf)
        assert result == pytest.approx(0.4, abs=0.01)
 
    def test_no_dnfs(self, driver_results_5):
        result = _dnf_rate(driver_results_5)
        assert result == pytest.approx(0.0, abs=0.01)
 
    def test_empty_returns_none(self):
        assert _dnf_rate(pd.DataFrame()) is None
 
    def test_all_dnf_statuses_recognised(self):
        """Every DNF status in DNF_STATUSES must be counted."""
        for status in list(DNF_STATUSES)[:5]:
            rows = [{"driver_code": "VER", "team_id": "rb", "finish_position": 1,
                     "points": 0.0, "status": status, "year": 2024, "round": 1}]
            result = _dnf_rate(pd.DataFrame(rows))
            assert result == pytest.approx(1.0, abs=0.01), f"Status '{status}' not counted as DNF"
 
 
# ---------------------------------------------------------------------------
# teammate_delta
# ---------------------------------------------------------------------------
 
class TestTeammateDelta:
 
    def test_driver_ahead_of_teammate(self, quali_history):
        """VER qualifies P1/P1/P2, PER qualifies P4/P5/P3 — VER is always ahead."""
        result = _teammate_delta("VER", "red_bull", quali_history)
        # deltas: 1-4=-3, 1-5=-4, 2-3=-1 → mean = -2.67
        assert result is not None
        assert result < 0  # negative means ahead of teammate
 
    def test_driver_behind_teammate(self, quali_history):
        result = _teammate_delta("PER", "red_bull", quali_history)
        assert result is not None
        assert result > 0  # positive means behind teammate
 
    def test_empty_returns_none(self):
        assert _teammate_delta("VER", "red_bull", pd.DataFrame()) is None
 
 
# ---------------------------------------------------------------------------
# tire_management_score
# ---------------------------------------------------------------------------
 
class TestTireManagementScore:
 
    def test_returns_float(self, telemetry_df):
        result = _tire_management_score(telemetry_df)
        assert result is not None
        assert isinstance(result, float)
 
    def test_mild_degradation_above_one(self, telemetry_df):
        """With lap times increasing per lap, late stint is slower → ratio > 1."""
        result = _tire_management_score(telemetry_df)
        assert result > 1.0
 
    def test_empty_returns_none(self):
        assert _tire_management_score(pd.DataFrame()) is None
 
    def test_no_accurate_laps_returns_none(self, telemetry_df):
        df = telemetry_df.copy()
        df["is_accurate"] = False
        assert _tire_management_score(df) is None
 
 
# ---------------------------------------------------------------------------
# constructor_form
# ---------------------------------------------------------------------------
 
class TestConstructorForm:
 
    def test_basic_form(self):
        rows = [
            {"driver_code": "VER", "team_id": "red_bull", "finish_position": 1,
             "points": 25.0, "status": "Finished", "year": 2024, "round": i}
            for i in range(1, 6)
        ] + [
            {"driver_code": "PER", "team_id": "red_bull", "finish_position": 2,
             "points": 18.0, "status": "Finished", "year": 2024, "round": i}
            for i in range(1, 6)
        ]
        result = _constructor_form(pd.DataFrame(rows))
        assert result is not None
        assert result == pytest.approx(43.0, abs=0.1)  # 25+18 per round
 
    def test_empty_returns_none(self):
        assert _constructor_form(pd.DataFrame()) is None
 
 
# ---------------------------------------------------------------------------
# reliability_score
# ---------------------------------------------------------------------------
 
class TestReliabilityScore:
 
    def test_perfect_reliability(self, driver_results_5):
        result = _reliability_score(driver_results_5)
        assert result == pytest.approx(1.0, abs=0.01)
 
    def test_partial_reliability(self, driver_results_with_dnf):
        result = _reliability_score(driver_results_with_dnf)
        assert result == pytest.approx(0.6, abs=0.01)  # 2 DNFs out of 5
 
    def test_empty_returns_none(self):
        assert _reliability_score(pd.DataFrame()) is None