"""
app/ml/storage/model_store.py
 
Supabase Storage integration for ML model artifact persistence.
 
WHY THIS EXISTS:
  Render free tier has no persistent disk — any file written to the
  container filesystem is destroyed on every redeploy or restart.
  Model artifacts (xgb_winner.json, xgb_podium.json, metadata.json)
  must survive redeploys. Supabase Storage is the source of truth.
 
FLOW:
  Training  → trainer.py saves locally → calls upload_model_artifacts()
  Startup   → loader.py checks local → missing → calls download_model_artifacts()
  API runs  → reads from in-memory models (no storage calls on requests)
 
SETUP (one-time):
  1. Go to Supabase Dashboard → Storage → New Bucket
  2. Name it "models", set to PRIVATE (not public)
  3. Set SUPABASE_URL and SUPABASE_SERVICE_KEY in env vars
"""
 
import os
from pathlib import Path
 
from app.core.logging import get_logger
 
logger = get_logger(__name__)
 
MODEL_FILES = ["xgb_winner.json", "xgb_podium.json", "metadata.json"]
BUCKET = "models"
 
 
def _get_client():
    """Lazy import — supabase-py only needed when storage is used."""
    try:
        from supabase import create_client
    except ImportError:
        raise RuntimeError(
            "supabase package not installed. Run: pip install supabase"
        )
 
    url = os.environ.get("SUPABASE_URL")
    key = os.environ.get("SUPABASE_SERVICE_KEY")
 
    if not url or not key:
        raise EnvironmentError(
            "SUPABASE_URL and SUPABASE_SERVICE_KEY must be set for model storage. "
            "These are different from DATABASE_URL — get them from Supabase Dashboard → Settings → API."
        )
    return create_client(url, key)
 
 def upload_model_artifacts(local_dir: Path) -> bool:
    """
    Upload all model artifacts from local_dir to Supabase Storage.
    Called by trainer.py after every successful training run.
 
    Returns True if all files uploaded, False if any failed.
    Does NOT raise — training succeeded, local files still usable
    until the next Render redeploy.
    """
    try:
        client = _get_client()
    except Exception as e:
        logger.error(f"Cannot connect to Supabase Storage: {e}")
        return False
 
    all_ok = True
    for filename in MODEL_FILES:
        local_path = local_dir / filename
        if not local_path.exists():
            logger.warning(f"Skipping upload — file not found: {local_path}")
            all_ok = False
            continue
 
        try:
            with open(local_path, "rb") as f:
                data = f.read()
 
            # upsert=True → overwrites existing file in the bucket
            client.storage.from_(BUCKET).upload(
                path=filename,
                file=data,
                file_options={"upsert": "true", "content-type": "application/octet-stream"},
            )
            logger.info(f"Uploaded {filename} to Supabase Storage (bucket='{BUCKET}')")
        except Exception as e:
            logger.error(f"Upload failed for {filename}: {e}")
            all_ok = False
 
    return all_ok