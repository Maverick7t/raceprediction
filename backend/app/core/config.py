import os
from dataclasses import dataclass
from dotenv import load_dotenv

load_dotenv()


@dataclass
class Config:
    DATABASE_URL: str
    FASTF1_CACHE_DIR: str
    ERGAST_BASE_URL: str
    OPENF1_BASE_URL: str
    ENVIRONMENT: str
    LOG_LEVEL: str

    @classmethod
    def from_env(cls) -> "Config":
        db_url = os.environ.get("DATABASE_URL")
        if not db_url:
            raise EnvironmentError("DATABASE_URL environment variable is required")
        return cls(
            DATABASE_URL=db_url,
            FASTF1_CACHE_DIR=os.environ.get("FASTF1_CACHE_DIR", "/tmp/fastf1_cache"),
            ERGAST_BASE_URL=os.environ.get("ERGAST_BASE_URL", "https://api.jolpi.ca/ergast/f1"),
            OPENF1_BASE_URL=os.environ.get("OPENF1_BASE_URL", "https://api.openf1.org/v1"),
            ENVIRONMENT=os.environ.get("ENVIRONMENT", "dev"),
            LOG_LEVEL=os.environ.get("LOG_LEVEL", "INFO"),
        )


config = Config.from_env()