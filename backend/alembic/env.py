from logging.config import fileConfig
import os
import sys

from dotenv import load_dotenv
from sqlalchemy import engine_from_config
from sqlalchemy import pool

from alembic import context

# Ensure the `backend` package is on sys.path so `from app...` imports work
# regardless of the current working directory when Alembic runs.
here = os.path.dirname(__file__)
backend_path = os.path.abspath(os.path.join(here, ".."))
if backend_path not in sys.path:
    sys.path.insert(0, backend_path)

# Load the repo-level .env file so DATABASE_URL is available when Alembic
# starts from the backend directory.
load_dotenv(os.path.abspath(os.path.join(here, "..", "..", ".env")))

from app.db.base import Base

# IMPORTANT:
# import all models so Alembic registers metadata
from app.db.models import *

config = context.config

# Allow overriding the URL in alembic.ini with the DATABASE_URL environment
# variable (useful for local Postgres/Supabase or CI). If DATABASE_URL is set
# it will replace the sqlalchemy.url value from the ini file.
db_url = os.environ.get("DATABASE_URL")
if db_url:
    config.set_main_option("sqlalchemy.url", db_url)

if config.config_file_name is not None:
    fileConfig(config.config_file_name)

target_metadata = Base.metadata


def run_migrations_offline() -> None:
    url = config.get_main_option(
        "sqlalchemy.url"
    )

    context.configure(
        url=url,
        target_metadata=target_metadata,
        literal_binds=True,
        dialect_opts={
            "paramstyle": "named"
        },
    )

    with context.begin_transaction():
        context.run_migrations()


def run_migrations_online() -> None:
    connectable = engine_from_config(
        config.get_section(
            config.config_ini_section,
            {}
        ),
        prefix="sqlalchemy.",
        poolclass=pool.NullPool,
    )

    with connectable.connect() as connection:
        context.configure(
            connection=connection,
            target_metadata=target_metadata,
        )

        with context.begin_transaction():
            context.run_migrations()


if context.is_offline_mode():
    run_migrations_offline()
else:
    run_migrations_online()