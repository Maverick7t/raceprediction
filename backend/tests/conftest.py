"""
conftest.py — shared fixtures for all Phase 1 tests.
 
Unit tests use SQLite in-memory (no network, no credentials needed).
Integration tests use real Postgres via DATABASE_URL env var.
"""
 
import os
import pytest
import pandas as pd
 
from sqlalchemy import create_engine, event
from sqlalchemy.orm import sessionmaker
 
os.environ.setdefault("DATABASE_URL", "sqlite:///:memory:")
os.environ.setdefault("ENVIRONMENT", "test")
os.environ.setdefault("LOG_LEVEL", "WARNING")
 
from app.db.base import Base
import app.db.models  # noqa — registers all models on Base.metadata
 
 
@pytest.fixture(scope="session")
def engine():
    _engine = create_engine(
        "sqlite:///:memory:",
        connect_args={"check_same_thread": False},
    )
 
    @event.listens_for(_engine, "connect")
    def set_pragma(dbapi_conn, _):
        dbapi_conn.cursor().execute("PRAGMA foreign_keys=ON")
 
    Base.metadata.create_all(bind=_engine)
    yield _engine
    _engine.dispose()
 