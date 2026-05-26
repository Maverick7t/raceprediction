"""
Unit tests — Phase 3 ML training.
 
WHEN TO RUN:
  After writing/changing trainer.py or evaluator.py
    pytest tests/unit/test_training.py -v
  CI: runs when files under app/ml/ change.
 
No real training happens in these tests.
No database calls. No MLflow calls.
All external dependencies are mocked.
"""
 
import json
import pytest
import pandas as pd
import numpy as np
from pathlib import Path
from unittest.mock import patch, MagicMock
 
from app.ml.training.evaluator import should_promote, PROMOTION_RULES, MINIMUM_THRESHOLDS
from app.ml.training.trainer import (
    _encode_and_clean,
    _evaluate,
    FEATURE_COLUMNS,
    CATEGORICAL_COLUMNS,
)

# ---------------------------------------------------------------------------
# Fixtures
# ---------------------------------------------------------------------------
 
@pytest.fixture
def strong_metrics():
    """Metrics that clearly beat production."""
    return {
        "winner_exact_accuracy": 0.35,
        "winner_top3_accuracy": 0.70,
        "podium_accuracy": 0.75,
        "training_rows": 500,
        "validation_races": 10,
        "run_id": "test_run_001",
    }
 
 
@pytest.fixture
def weak_metrics():
    """Metrics below minimum thresholds."""
    return {
        "winner_exact_accuracy": 0.05,
        "winner_top3_accuracy": 0.20,
        "podium_accuracy": 0.40,
        "training_rows": 50,
        "validation_races": 5,
        "run_id": "test_run_002",
    }
 
 
@pytest.fixture
def production_metrics():
    return {
        "winner_exact_accuracy": 0.28,
        "winner_top3_accuracy": 0.55,
        "podium_accuracy": 0.65,
    }
 
 
@pytest.fixture
def sample_training_df():
    """Minimal training DataFrame with all required columns."""
    np.random.seed(42)
    n = 100
    rows = []
    for i in range(n):
        rows.append({
            "race_key": f"race_{i % 20}",
            "driver_code": np.random.choice(["VER", "LEC", "HAM", "SAI", "NOR"]),
            "driver_name": "Test Driver",
            "team_id": np.random.choice(["red_bull", "ferrari", "mercedes"]),
            "circuit_id": np.random.choice(["bahrain", "monaco", "silverstone"]),
            "year": 2023 if i < 80 else 2024,
            "round": (i % 20) + 1,
            "feature_version": "v1",
            "avg_finish_last_5": np.random.uniform(1, 20),
            "avg_quali_last_5": np.random.uniform(1, 20),
            "podium_rate": np.random.uniform(0, 1),
            "dnf_rate": np.random.uniform(0, 0.3),
            "wet_weather_score": 5.0,
            "teammate_delta": np.random.uniform(-3, 3),
            "tire_management_score": np.random.uniform(0.95, 1.1),
            "constructor_form": np.random.uniform(10, 50),
            "reliability_score": np.random.uniform(0.7, 1.0),
            "overtaking_difficulty": np.random.uniform(2, 9),
            "tire_deg_factor": np.random.uniform(2, 8),
            "safety_car_probability": np.random.uniform(0.2, 0.6),
            "qualifying_position": np.random.randint(1, 21),
            "qualifying_delta_to_pole": np.random.uniform(0, 3),
            "finish_position": np.random.randint(1, 21),
            "is_winner": 1 if i % 20 == 0 else 0,
            "is_podium": 1 if i % 20 <= 2 else 0,
            "pitstop_avg": None,
        })
    return pd.DataFrame(rows)

# ---------------------------------------------------------------------------
# Promotion logic
# ---------------------------------------------------------------------------
 
class TestShouldPromote:
 
    def test_no_production_model_always_promotes(self, strong_metrics):
        with patch("app.ml.training.evaluator._get_production_metrics", return_value=None):
            promote, reason = should_promote(strong_metrics)
        assert promote is True
        assert "No production model" in reason
 
    def test_below_minimum_threshold_never_promotes(self, weak_metrics):
        with patch("app.ml.training.evaluator._get_production_metrics", return_value=None):
            promote, reason = should_promote(weak_metrics)
        assert promote is False
        assert "minimum threshold" in reason
 
    def test_beats_production_on_2_metrics_promotes(self, strong_metrics, production_metrics):
        with patch("app.ml.training.evaluator._get_production_metrics", return_value=production_metrics):
            promote, reason = should_promote(strong_metrics)
        assert promote is True
 
    def test_marginal_improvement_does_not_promote(self, production_metrics):
        """Improvement below MIN_IMPROVEMENT on all metrics → no promotion."""
        marginal = {
            "winner_exact_accuracy": production_metrics["winner_exact_accuracy"] + 0.001,
            "winner_top3_accuracy": production_metrics["winner_top3_accuracy"] + 0.001,
            "podium_accuracy": production_metrics["podium_accuracy"] + 0.001,
            "run_id": "marginal_run",
        }
        with patch("app.ml.training.evaluator._get_production_metrics", return_value=production_metrics):
            promote, reason = should_promote(marginal)
        assert promote is False
 
    def test_promotion_requires_min_2_metrics(self, production_metrics):
        """Beats production on only 1 metric → no promotion."""
        one_metric = {
            "winner_exact_accuracy": production_metrics["winner_exact_accuracy"] + 0.10,  # beats
            "winner_top3_accuracy": production_metrics["winner_top3_accuracy"] - 0.05,    # worse
            "podium_accuracy": production_metrics["podium_accuracy"] - 0.05,              # worse
            "run_id": "one_metric_run",
        }
        with patch("app.ml.training.evaluator._get_production_metrics", return_value=production_metrics):
            promote, reason = should_promote(one_metric)
        assert promote is False
 

 # ---------------------------------------------------------------------------
# should_retrain
# ---------------------------------------------------------------------------
 
class TestShouldRetrain:
 
    def test_no_metadata_returns_true(self):
        with patch("app.ml.training.evaluator._get_last_trained_at", return_value=None):
            from app.ml.training.evaluator import should_retrain
            with patch("app.ml.training.evaluator.get_session") as mock_session:
                result = should_retrain()
        assert result is True
 
    def test_enough_new_results_returns_true(self):
        with patch("app.ml.training.evaluator._get_last_trained_at", return_value="2024-01-01T00:00:00+00:00"):
            mock_session = MagicMock()
            mock_session.__enter__ = MagicMock(return_value=mock_session)
            mock_session.__exit__ = MagicMock(return_value=False)
            mock_session.execute.return_value.scalar.return_value = 5
 
            with patch("app.ml.training.evaluator.get_session", return_value=mock_session):
                from app.ml.training.evaluator import should_retrain
                result = should_retrain()
        assert result is True
 
    def test_not_enough_results_returns_false(self):
        with patch("app.ml.training.evaluator._get_last_trained_at", return_value="2024-01-01T00:00:00+00:00"):
            mock_session = MagicMock()
            mock_session.__enter__ = MagicMock(return_value=mock_session)
            mock_session.__exit__ = MagicMock(return_value=False)
            mock_session.execute.return_value.scalar.return_value = 2  # only 2, need 3
 
            with patch("app.ml.training.evaluator.get_session", return_value=mock_session):
                from app.ml.training.evaluator import should_retrain
                result = should_retrain()
        assert result is False