"""
app/ml/inference/loader.py
 
Model artifact loader with cloud-fallback for Render deployments.
 
LOAD ORDER (on every API startup):
  1. Check local models/ directory
     → Fast path. Works in dev and immediately after training.
  2. If local missing → download from Supabase Storage
     → Handles Render redeploys: new container auto-downloads artifacts.
  3. If both fail → raise RuntimeError
     → Application must NOT start without a model. Render will keep
        the old container running (zero-downtime) until the new one
        passes its health check.
 
This is called ONCE at startup. Result is stored in memory.
Never call this on a per-request basis.
"""
 
import json
from pathlib import Path
 
from xgboost import XGBClassifier
 
from app.core.logging import get_logger
from app.ml.storage.model_store import download_model_artifacts, artifacts_exist_remotely
 
logger = get_logger(__name__)
 
_REQUIRED_FILES = ["xgb_winner.json", "xgb_podium.json", "metadata.json"]
 
 
class ModelArtifacts:
    """
    Container for all loaded model artifacts.
    Kept in memory for the lifetime of the API process.
    """
 
    def __init__(
        self,
        winner_model: XGBClassifier,
        podium_model: XGBClassifier,
        metadata: dict,
    ):
        self.winner_model = winner_model
        self.podium_model = podium_model
        self.metadata = metadata
 
        # Derived — used by inference engine and health endpoint
        self.feature_columns: list[str] = metadata.get("feature_columns", [])
        self.model_version: str = metadata.get("model_version", "unknown")
        self.feature_version: str = metadata.get("feature_version", "v1")
        self.encoder_classes: dict = metadata.get("encoder_classes", {})
        self.is_production: bool = metadata.get("is_production", False)
 
    def __repr__(self) -> str:
        return (
            f"<ModelArtifacts version={self.model_version!r} "
            f"features={len(self.feature_columns)} "
            f"production={self.is_production}>"
        )