"""
app/ml/inference/loader.py

Thread-safe singleton for the InferenceEngine.
Called at FastAPI startup — blocks until models are loaded.
Call reload_engine() after a model promotion to hot-swap without restart.
"""

import threading
from pathlib import Path
import os

from app.ml.inference.engine import InferenceEngine
from app.core.logging import get_logger

logger = get_logger(__name__)

_lock = threading.Lock()
_engine: InferenceEngine | None = None

_MODELS_DIR = Path(os.environ.get("MODELS_DIR", "models"))


def get_engine() -> InferenceEngine:
    """Return the loaded engine. Raises if models are not yet loaded."""
    global _engine
    if _engine is None:
        with _lock:
            if _engine is None:
                logger.info(f"Loading inference engine from {_MODELS_DIR}")
                _engine = InferenceEngine(_MODELS_DIR)
    return _engine

def reload_engine() -> InferenceEngine:
    """Hot-swap the engine — used after model promotion. Thread-safe."""
    global _engine
    with _lock:
        logger.info("Reloading inference engine")
        _engine = InferenceEngine(_MODELS_DIR)
    logger.info("Inference engine reloaded")
    return _engine


def engine_is_loaded() -> bool:
    return _engine is not None