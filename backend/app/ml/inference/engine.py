"""
app/ml/inference/engine.py

Loads trained model artifacts from models/ and runs predictions.
Stateless after __init__ — safe to call predict() from any thread.

Never import FastAPI or Prefect here. This module is ML-only.
"""

import json
from pathlib import Path

import numpy as np
import pandas as pd
from sklearn.preprocessing import LabelEncoder
from xgboost import XGBClassifier

from app.core.logging import get_logger

logger = get_logger(__name__)


class InferenceEngine:

    def __init__(self, models_dir: Path):
        metadata_path = models_dir / "metadata.json"
        if not metadata_path.exists():
            raise FileNotFoundError(f"metadata.json not found in {models_dir}")

        with open(metadata_path) as f:
            self._metadata = json.load(f)

        self.model_version: str = self._metadata["model_version"]
        self.feature_version: str = self._metadata["feature_version"]
        self.feature_columns: list[str] = self._metadata["feature_columns"]
        self.categorical_columns: list[str] = self._metadata["categorical_columns"]

        # Rebuild label encoders from saved classes
        self._encoders: dict[str, LabelEncoder] = {}
        for col, classes in self._metadata["encoder_classes"].items():
            enc = LabelEncoder()
            enc.classes_ = np.array(classes)
            self._encoders[col] = enc

        # Load XGBoost models
        self._winner_model = XGBClassifier()
        self._winner_model.load_model(str(models_dir / "xgb_winner.json"))

        self._podium_model = XGBClassifier()
        self._podium_model.load_model(str(models_dir / "xgb_podium.json"))

        logger.info(
            f"InferenceEngine loaded "
            f"model_version={self.model_version} "
            f"feature_version={self.feature_version} "
            f"features={len(self.feature_columns)}"
        )
