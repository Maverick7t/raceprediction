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

# ----------------Public------------------------------------------------------------------

    def predict(self, features_df: pd.DataFrame) -> pd.DataFrame:
        """
        Run winner + podium prediction for every driver in features_df.

        Returns the same DataFrame with three new columns:
          predicted_winner_prob  — float [0, 1]
          predicted_podium_prob  — float [0, 1]
          predicted_rank         — int 1-20, ranked by winner_prob descending

        Sorted by predicted_rank ascending (winner first).
        """
        if features_df.empty:
            logger.warning("predict() called with empty DataFrame")
            return features_df

        df = features_df.copy()
        df = self._encode_categoricals(df)
        df = self._fill_numeric_nulls(df)

        available = [c for c in self.feature_columns if c in df.columns]
        missing = set(self.feature_columns) - set(available)
        if missing:
            logger.warning(f"Missing feature columns at inference: {missing}")

        X = df[available]

        df["predicted_winner_prob"] = self._winner_model.predict_proba(X)[:, 1]
        df["predicted_podium_prob"] = self._podium_model.predict_proba(X)[:, 1]
        df["predicted_rank"] = (
            df["predicted_winner_prob"]
            .rank(ascending=False, method="min")
            .astype(int)
        )

        logger.info(
            f"Inference complete: {len(df)} drivers, "
            f"race_key={df['race_key'].iloc[0] if 'race_key' in df.columns else 'unknown'}"
        )
        return df.sort_values("predicted_rank").reset_index(drop=True)
    
#--------------------Internal-----------------------------------------------------------------

    def _encode_categoricals(self, df: pd.DataFrame) -> pd.DataFrame:
        for col in self.categorical_columns:
            if col not in df.columns:
                continue
            enc = self._encoders.get(col)
            if enc is None:
                continue

            known = set(enc.classes_)

            def _safe_encode(v, enc=enc, known=known):
                if pd.isna(v) or v not in known:
                    return 0  # unknown → default to 0
                return int(enc.transform([v])[0])

            df[f"{col}_encoded"] = df[col].map(_safe_encode)
        return df

    def _fill_numeric_nulls(self, df: pd.DataFrame) -> pd.DataFrame:
        base_cols = self._metadata.get("base_feature_columns", [])
        for col in base_cols:
            if col in df.columns and df[col].isna().any():
                median = df[col].median()
                df[col] = df[col].fillna(median if pd.notna(median) else 0.0)
        return df
