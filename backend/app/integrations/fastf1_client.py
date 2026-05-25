"""
FastF1 integration client.
 
Responsibility: load qualifying and race session data from FastF1.
All DataFrame columns are normalised here before leaving this module.
Nothing outside this module imports fastf1 directly.
 
Cache behaviour:
  FastF1 writes to disk on first load. Subsequent loads for the same
  session hit the disk cache and are fast (~1s vs 30–60s cold).
  Cache dir is configurable via FASTF1_CACHE_DIR env var.
  In CI/CD, set FASTF1_CACHE_DIR to a path that is NOT in /tmp if you
  want the cache to persist across workflow runs (use a cache action).
"""
 
from pathlib import Path
 
import fastf1
import pandas as pd
 
from app.core.config import config
from app.core.exceptions import IngestionError
from app.core.logging import get_logger
 
logger = get_logger(__name__)
 
# Configure FastF1 cache once at import time
Path(config.FASTF1_CACHE_DIR).mkdir(parents=True, exist_ok=True)
fastf1.Cache.enable_cache(config.FASTF1_CACHE_DIR)