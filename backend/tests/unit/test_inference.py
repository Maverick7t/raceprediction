"""
Unit tests — InferenceEngine and prediction_service.
No real model files needed — engine is mocked.
"""

import pandas as pd
import numpy as np
import pytest
from unittest.mock import patch, MagicMock


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