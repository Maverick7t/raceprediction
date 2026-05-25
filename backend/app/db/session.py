from sqlalchemy import create_engine, text
from sqlalchemy.orm import sessionmaker, Session
from contextlib import contextmanager
from typing import Generator

from app.core.config import config
from app.core.logging import get_logger

logger = get_logger(__name__)

# ---------------------------------------------------------------------------
# Engine
# Pool tuned for Supabase free tier (max 15 direct connections).
# ---------------------------------------------------------------------------
engine = create_engine(
    config.DATABASE_URL,
    pool_size=2,
    max_overflow=3,
    pool_timeout=30,
    pool_recycle=1800,
    pool_pre_ping=True,   # detect stale connections before use
    echo=False,
)

SessionLocal = sessionmaker(
    bind=engine,
    autoflush=False,
    autocommit=False,
    expire_on_commit=False,
)


@contextmanager
def get_session() -> Generator[Session, None, None]:
    """
    Context manager for a database session.
    Always use this — never instantiate SessionLocal directly.

    Usage:
        with get_session() as session:
            session.add(row)
            session.commit()

    Rolls back automatically on exception.
    Closes the session on exit regardless.
    """
    session = SessionLocal()
    try:
        yield session
        session.commit()
    except Exception:
        session.rollback()
        raise
    finally:
        session.close()


def check_connection() -> bool:
    """
    Verify database is reachable.
    Used by /health/db endpoint and startup checks.
    Returns True on success, False on failure (never raises).
    """
    try:
        with engine.connect() as conn:
            conn.execute(text("SELECT 1"))
        return True
    except Exception as e:
        logger.error(f"Database connection check failed: {e}")
        return False