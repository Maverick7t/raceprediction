"""
app/ml/training/trainer.py
 
Trains two XGBoost classifiers:
  1. winner_model   — predicts race winner (binary: is_winner)
  2. podium_model   — predicts podium finish (binary: is_podium)
 
Training rules:
  - Time-based split ONLY — never random split (leaks future data)
  - Reads from features_by_race where finish_position IS NOT NULL
  - Saves artifacts to models/ directory
  - Registers run in MLflow
  - Never auto-promotes to production — evaluator decides that separately
 
Artifact files written:
  models/xgb_winner.json
  models/xgb_podium.json
  models/metadata.json       — feature columns, label encoders, version info
"""
 
import json
import os
from datetime import datetime, timezone
from pathlib import Path
 
import mlflow
import numpy as np
import pandas as pd
from sklearn.preprocessing import LabelEncoder
from xgboost import XGBClassifier
 
from app.core.logging import get_logger
from app.db.repositories.feature_repo import FeatureRepository, CURRENT_FEATURE_VERSION
 
logger = get_logger(__name__)
 
MODELS_DIR = Path(os.environ.get("MODELS_DIR", "models"))
MODELS_DIR.mkdir(exist_ok=True)
 
# Feature columns the model trains on
# Changing this list = bump CURRENT_FEATURE_VERSION in feature_repo.py
FEATURE_COLUMNS = [
    "avg_finish_last_5",
    "avg_quali_last_5",
    "podium_rate",
    "dnf_rate",
    "wet_weather_score",
    "teammate_delta",
    "tire_management_score",
    "constructor_form",
    "reliability_score",
    "overtaking_difficulty",
    "tire_deg_factor",
    "safety_car_probability",
    "qualifying_position",
    "qualifying_delta_to_pole",
]

# Categorical columns that need label encoding
CATEGORICAL_COLUMNS = ["driver_code", "team_id", "circuit_id"]
 
# Validation split — last N races held out for evaluation
VALIDATION_RACES = 10
 
 
def retrain_from_supabase(
    feature_version: str = CURRENT_FEATURE_VERSION,
    from_year: int = 2018,
    mlflow_experiment: str = "f1_prediction",
) -> dict:
    """
    Full training pipeline. Called by the Prefect retrain flow.
 
    Returns metrics dict:
      {
        "winner_top3_accuracy": float,
        "winner_exact_accuracy": float,
        "podium_accuracy": float,
        "training_rows": int,
        "validation_races": int,
        "run_id": str,
      }
    """
    logger.info(f"Retraining started feature_version={feature_version} from_year={from_year}")