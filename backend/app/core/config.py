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


    # --- Derived (not from env directly) ---
    @property
    def models_path(self) -> Path:
        return Path(self.MODELS_DIR)
 
    @property
    def cors_origins(self) -> list[str]:
        """
        CORS allowed origins.
        In dev: localhost ports for Vite.
        In prod: the configured FRONTEND_URL only.
        """
        origins = [self.FRONTEND_URL]
        if not self.is_production:
            origins += [
                "http://localhost:5173",
                "http://localhost:3000",
                "http://127.0.0.1:5173",
            ]
        return origins
 
    @property
    def is_production(self) -> bool:
        return self.ENVIRONMENT.lower() == "prod"
 
    @property
    def supabase_storage_configured(self) -> bool:
        """True if Supabase Storage credentials are available."""
        return bool(self.SUPABASE_URL and self.SUPABASE_SERVICE_KEY)
 
    @classmethod
    def from_env(cls) -> "Config":
        db_url = os.environ.get("DATABASE_URL")
        if not db_url:
            raise EnvironmentError(
                "DATABASE_URL is required. "
                "Get it from Supabase Dashboard → Settings → Database → Connection string (Transaction pooler)."
            )
 
        return cls(
            DATABASE_URL=db_url,
            SUPABASE_URL=os.environ.get("SUPABASE_URL", ""),
            SUPABASE_SERVICE_KEY=os.environ.get("SUPABASE_SERVICE_KEY", ""),
            FASTF1_CACHE_DIR=os.environ.get("FASTF1_CACHE_DIR", "/tmp/fastf1_cache"),
            ERGAST_BASE_URL=os.environ.get("ERGAST_BASE_URL", "https://api.jolpi.ca/ergast/f1"),
            OPENF1_BASE_URL=os.environ.get("OPENF1_BASE_URL", "https://api.openf1.org/v1"),
            MODELS_DIR=os.environ.get("MODELS_DIR", "models"),
            MODEL_STORAGE_BUCKET=os.environ.get("MODEL_STORAGE_BUCKET", "models"),
            MLFLOW_TRACKING_URI=os.environ.get("MLFLOW_TRACKING_URI", "mlruns"),
            API_SECRET_KEY=os.environ.get("API_SECRET_KEY", ""),
            FRONTEND_URL=os.environ.get("FRONTEND_URL", "http://localhost:5173"),
            SENTRY_DSN=os.environ.get("SENTRY_DSN", ""),
            BETTERSTACK_TOKEN=(
                os.environ.get("BETTERSTACK_TOKEN")
                or os.environ.get("LOGTAIL_SOURCE_TOKEN", "")
            ),
            ENVIRONMENT=os.environ.get("ENVIRONMENT", "dev"),
            LOG_LEVEL=os.environ.get("LOG_LEVEL", "INFO"),
            PORT=int(os.environ.get("PORT", "8000")),
        )
 
 
config = Config.from_env()