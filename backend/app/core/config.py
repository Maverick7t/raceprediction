"""
app/core/config.py
 
Central configuration. All env vars are declared here.
No other file calls os.environ directly — import config instead.
 
Environment separation:
  dev  → .env (local) → points to dev Supabase project
  prod → Render env vars → points to prod Supabase project
 
Never commit .env. Never hardcode secrets here.
"""
 
import os
from dataclasses import dataclass, field
from pathlib import Path
from dotenv import load_dotenv
 
load_dotenv()
 
 
@dataclass
class Config:
    # --- Database ---
    DATABASE_URL: str
 
    # --- Supabase (Storage + optionally direct client) ---
    # Get from: Supabase Dashboard → Settings → API
    SUPABASE_URL: str = ""
    SUPABASE_SERVICE_KEY: str = ""   # service_role key — NOT anon key
 
    # --- External API integrations ---
    FASTF1_CACHE_DIR: str = "/tmp/fastf1_cache"
    ERGAST_BASE_URL: str = "https://api.jolpi.ca/ergast/f1"
    OPENF1_BASE_URL: str = "https://api.openf1.org/v1"
 
    # --- ML ---
    MODELS_DIR: str = "models"                  # local path, gitignored
    MODEL_STORAGE_BUCKET: str = "models"        # Supabase Storage bucket name
    MLFLOW_TRACKING_URI: str = "mlruns"         # local mlruns/ in dev
 
    # --- API ---
    API_SECRET_KEY: str = ""                    # for write-endpoint bearer auth
    FRONTEND_URL: str = "http://localhost:5173" # Vercel URL in prod
 
    # --- Observability ---
    SENTRY_DSN: str = ""
    BETTERSTACK_TOKEN: str = ""                 # also accepts LOGTAIL_SOURCE_TOKEN
 
    # --- Runtime ---
    ENVIRONMENT: str = "dev"
    LOG_LEVEL: str = "INFO"
    PORT: int = 8000