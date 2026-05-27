"""
Unit tests — InferenceEngine and prediction_service.
No real model files needed — engine is mocked.
"""

import pandas as pd
import numpy as np
import pytest
from unittest.mock import patch, MagicMock
from app.db.repositories.prediction_repo import PredictionRepository



@pytest.fixture
def sample_features_df():
    np.random.seed(0)
    return pd.DataFrame([
        {
            "race_key": "bahrain_grand_prix_2024",
            "driver_code": "VER", "driver_name": "Max Verstappen",
            "team_id": "red_bull", "circuit_id": "bahrain",
            "qualifying_position": 1,
            "avg_finish_last_5": 2.0, "avg_quali_last_5": 1.5,
            "podium_rate": 0.8, "dnf_rate": 0.0,
            "teammate_delta": -3.0, "constructor_form": 45.0,
            "reliability_score": 1.0, "feature_version": "v1",
        },
        {
            "race_key": "bahrain_grand_prix_2024",
            "driver_code": "LEC", "driver_name": "Charles Leclerc",
            "team_id": "ferrari", "circuit_id": "bahrain",
            "qualifying_position": 2,
            "avg_finish_last_5": 4.0, "avg_quali_last_5": 3.0,
            "podium_rate": 0.4, "dnf_rate": 0.1,
            "teammate_delta": 1.0, "constructor_form": 30.0,
            "reliability_score": 0.9, "feature_version": "v1",
        },
    ])

class TestPredictionService:

    def test_run_inference_returns_summary(self, sample_features_df):
        mock_engine = MagicMock()
        mock_engine.model_version = "baseline_v1"
        mock_engine.feature_version = "v1"

        result_df = sample_features_df.copy()
        result_df["predicted_winner_prob"] = [0.7, 0.3]
        result_df["predicted_podium_prob"] = [0.9, 0.6]
        result_df["predicted_rank"] = [1, 2]
        mock_engine.predict.return_value = result_df

        mock_feature_repo = MagicMock()
        mock_feature_repo.get_features_for_race.return_value = sample_features_df

        mock_prediction_repo = MagicMock()
        mock_prediction_repo.upsert_predictions.return_value = 2

        with patch("app.services.prediction_service.get_engine", return_value=mock_engine), \
             patch("app.services.prediction_service._feature_repo", mock_feature_repo), \
             patch("app.services.prediction_service._prediction_repo", mock_prediction_repo):

            from app.services.prediction_service import run_inference_for_race
            result = run_inference_for_race("bahrain_grand_prix_2024")

        assert result["status"] == "completed"
        assert result["rows_stored"] == 2
        assert result["model_version"] == "baseline_v1"

    def test_run_inference_no_features(self):
        mock_engine = MagicMock()
        mock_engine.feature_version = "v1"

        mock_feature_repo = MagicMock()
        mock_feature_repo.get_features_for_race.return_value = pd.DataFrame()

        with patch("app.services.prediction_service.get_engine", return_value=mock_engine), \
             patch("app.services.prediction_service._feature_repo", mock_feature_repo):

            from app.services.prediction_service import run_inference_for_race
            result = run_inference_for_race("missing_race_2099")

        assert result["status"] == "no_features"
        assert result["rows_stored"] == 0


class TestPredictionRepo:
    def test_prepare_rows_converts_numpy(self):
        df = pd.DataFrame([{
            "race_key": "bahrain_2024", "driver_code": "VER",
            "driver_name": "Verstappen", "team_id": "red_bull",
            "qualifying_position": np.int64(1),
            "predicted_winner_prob": np.float64(0.75),
            "predicted_podium_prob": np.float64(0.90),
            "predicted_rank": np.int64(1),
            "model_version": "baseline_v1", "feature_version": "v1",
        }])
        rows = PredictionRepository._prepare_rows(df)
        assert isinstance(rows[0]["qualifying_position"], int)
        assert isinstance(rows[0]["predicted_winner_prob"], float)

    def test_prepare_rows_nan_to_none(self):
        df = pd.DataFrame([{
            "race_key": "r", "driver_code": "VER", "driver_name": "V",
            "team_id": "rb", "qualifying_position": float("nan"),
            "predicted_winner_prob": 0.5, "predicted_podium_prob": 0.7,
            "predicted_rank": 1, "model_version": "v1", "feature_version": "v1",
        }])
        rows = PredictionRepository._prepare_rows(df)
        assert rows[0]["qualifying_position"] is None