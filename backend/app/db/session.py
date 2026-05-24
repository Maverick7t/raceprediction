import os

from dotenv import load_dotenv
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker

load_dotenv()

DATABASE_URL = os.getenv("DATABASE_URL")

if not DATABASE_URL:
    raise ValueError("DATABASE_URL environment variable is not set")

engine = create_engine(
    DATABASE_URL,

    pool_size=2,
    max_overflow=3,
    pool_timeout=30,
    pool_recycle=1800

    pool_pre_ping=True
    echo=False
)

SessionLocal = sessionmaker(
    bind=engine,
    autocommit=False,
    expire_on_commit=False
)