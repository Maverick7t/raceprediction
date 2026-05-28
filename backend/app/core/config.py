import os
from dataclasses import dataclass, field
from dotenv import load_dotenv

load_dotenv()


@dataclass
class Config:
    # ------------------------------------------------------------------ Core
    DATABASE_URL: str
    ENVIRONMENT: str          # "dev" | "prod"
    LOG_LEVEL: str

    # ------------------------------------------------------------------ External APIs
    FASTF1_CACHE_DIR: str
    ERGAST_BASE_URL: str
    OPENF1_BASE_URL: str

    # ------------------------------------------------------------------ Observability
    SENTRY_DSN: str | None          # None → Sentry disabled (dev default)
    BETTERSTACK_TOKEN: str | None   # Logtail source token for log shipping

    # ------------------------------------------------------------------ Security
    API_SECRET_KEY: str | None      # Bearer token for write endpoints
    FRONTEND_URL: str               # Allowed CORS origin in prod

    # ------------------------------------------------------------------ Model
    MODELS_DIR: str

    @classmethod
    def from_env(cls) -> "Config":
        db_url = os.environ.get("DATABASE_URL")
        if not db_url:
            raise EnvironmentError("DATABASE_URL environment variable is required")

        return cls(
            DATABASE_URL=db_url,
            ENVIRONMENT=os.environ.get("ENVIRONMENT", "dev"),
            LOG_LEVEL=os.environ.get("LOG_LEVEL", "INFO"),
            FASTF1_CACHE_DIR=os.environ.get("FASTF1_CACHE_DIR", "/tmp/fastf1_cache"),
            ERGAST_BASE_URL=os.environ.get(
                "ERGAST_BASE_URL", "https://api.jolpi.ca/ergast/f1"
            ),
            OPENF1_BASE_URL=os.environ.get(
                "OPENF1_BASE_URL", "https://api.openf1.org/v1"
            ),
            SENTRY_DSN=os.environ.get("SENTRY_DSN"),               # None if unset
            BETTERSTACK_TOKEN=os.environ.get("BETTERSTACK_TOKEN"),  # None if unset
            API_SECRET_KEY=os.environ.get("API_SECRET_KEY"),        # None → auth disabled
            FRONTEND_URL=os.environ.get("FRONTEND_URL", "http://localhost:5173"),
            MODELS_DIR=os.environ.get("MODELS_DIR", "models"),
        )

    @property
    def is_production(self) -> bool:
        return self.ENVIRONMENT == "prod"

    @property
    def cors_origins(self) -> list[str]:
        """
        Dev: allow localhost on common Vite/React ports.
        Prod: allow only the configured Vercel frontend URL.
        """
        if self.is_production:
            return [self.FRONTEND_URL]
        return [
            "http://localhost:5173",
            "http://localhost:3000",
            "http://127.0.0.1:5173",
        ]


config = Config.from_env()