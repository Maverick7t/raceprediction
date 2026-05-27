"""add predictions and standings tables

Revision ID: 0003_add_predictions_standings
Revises: 17cb21c264fe
Create Date: 2025-05-27
"""
from alembic import op
import sqlalchemy as sa

revision = "0003_add_predictions_standings"
down_revision = "17cb21c264fe"
branch_labels = None
depends_on = None


def upgrade() -> None:
    op.create_table(
        "predictions",
        sa.Column("id", sa.BigInteger(), nullable=False),
        sa.Column("race_key", sa.Text(), nullable=False),
        sa.Column("driver_code", sa.Text(), nullable=False),
        sa.Column("driver_name", sa.Text(), nullable=False),
        sa.Column("team_id", sa.Text(), nullable=False),
        sa.Column("qualifying_position", sa.SmallInteger(), nullable=True),
        sa.Column("predicted_winner_prob", sa.Float(), nullable=False),
        sa.Column("predicted_podium_prob", sa.Float(), nullable=False),
        sa.Column("predicted_rank", sa.SmallInteger(), nullable=False),
        sa.Column("model_version", sa.Text(), nullable=False),
        sa.Column("feature_version", sa.Text(), nullable=False),
        sa.Column(
            "generated_at",
            sa.TIMESTAMP(timezone=True),
            server_default=sa.text("now()"),
            nullable=False,
        ),
        sa.PrimaryKeyConstraint("id", name=op.f("pk_predictions")),
        sa.UniqueConstraint("race_key", "driver_code", name="predictions_race_driver_unique"),
    )
    op.create_index("idx_predictions_race_key", "predictions", ["race_key"])
    op.create_index("idx_predictions_generated_at", "predictions", ["generated_at"])

    op.create_table(
        "driver_standings_cache",
        sa.Column("id", sa.BigInteger(), nullable=False),
        sa.Column("year", sa.SmallInteger(), nullable=False),
        sa.Column("round", sa.SmallInteger(), nullable=True),
        sa.Column("driver_code", sa.Text(), nullable=False),
        sa.Column("driver_id", sa.Text(), nullable=False),
        sa.Column("driver_name", sa.Text(), nullable=False),
        sa.Column("team", sa.Text(), nullable=False),
        sa.Column("position", sa.SmallInteger(), nullable=False),
        sa.Column("points", sa.Float(), nullable=False),
        sa.Column("wins", sa.Integer(), nullable=False),
        sa.Column(
            "synced_at",
            sa.TIMESTAMP(timezone=True),
            server_default=sa.text("now()"),
            nullable=False,
        ),
        sa.PrimaryKeyConstraint("id", name=op.f("pk_driver_standings_cache")),
        sa.UniqueConstraint("year", "driver_code", name="driver_standings_year_driver_unique"),
    )
    op.create_index("idx_driver_standings_year", "driver_standings_cache", ["year"])

    op.create_table(
        "constructor_standings_cache",
        sa.Column("id", sa.BigInteger(), nullable=False),
        sa.Column("year", sa.SmallInteger(), nullable=False),
        sa.Column("round", sa.SmallInteger(), nullable=True),
        sa.Column("team_id", sa.Text(), nullable=False),
        sa.Column("team", sa.Text(), nullable=False),
        sa.Column("position", sa.SmallInteger(), nullable=False),
        sa.Column("points", sa.Float(), nullable=False),
        sa.Column("wins", sa.Integer(), nullable=False),
        sa.Column(
            "synced_at",
            sa.TIMESTAMP(timezone=True),
            server_default=sa.text("now()"),
            nullable=False,
        ),
        sa.PrimaryKeyConstraint("id", name=op.f("pk_constructor_standings_cache")),
        sa.UniqueConstraint("year", "team_id", name="constructor_standings_year_team_unique"),
    )
    op.create_index("idx_constructor_standings_year", "constructor_standings_cache", ["year"])

    def downgrade() -> None:
    op.drop_table("constructor_standings_cache")
    op.drop_table("driver_standings_cache")
    op.drop_table("predictions")