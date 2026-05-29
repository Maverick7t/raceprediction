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
    
    def load_model_artifacts(models_dir: Path) -> ModelArtifacts:
    """
    Load winner model, podium model, and metadata.
 
    Tries local directory first; falls back to Supabase Storage download.
    Raises RuntimeError if neither source has the artifacts — this is
    intentional: the API should NOT start without a valid model.
 
    Args:
        models_dir: Path to local models directory (from config.MODELS_DIR)
 
    Returns:
        ModelArtifacts instance ready for inference
 
    Raises:
        RuntimeError: if artifacts cannot be loaded from any source
    """
    # --- Attempt 1: local ---
    if _local_artifacts_complete(models_dir):
        logger.info(f"Loading model artifacts from local directory: {models_dir}")
        return _load_from_disk(models_dir)
 
    logger.warning(
        f"Local model artifacts incomplete in {models_dir} — "
        "attempting download from Supabase Storage"
    )
 
    # --- Attempt 2: Supabase Storage → download → load locally ---
    success = download_model_artifacts(models_dir)
 
    if success and _local_artifacts_complete(models_dir):
        logger.info("Model artifacts downloaded from Supabase Storage and loaded")
        return _load_from_disk(models_dir)
 
    # --- Both failed: give an actionable error message ---
    remote_available = artifacts_exist_remotely()
    if remote_available:
        raise RuntimeError(
            "Model artifacts exist in Supabase Storage but download failed. "
            "Check SUPABASE_URL, SUPABASE_SERVICE_KEY, and network connectivity."
        )
    else:
        raise RuntimeError(
            f"No model artifacts found locally ({models_dir}) or in Supabase Storage. "
            "Run the training pipeline first:\n"
            "  python -m workers.flows.retrain_flow\n"
            "Then ensure SUPABASE_URL and SUPABASE_SERVICE_KEY are set so "
            "artifacts are uploaded after training."
        )