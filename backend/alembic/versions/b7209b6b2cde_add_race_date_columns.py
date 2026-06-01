"""add race_date columns

Revision ID: b7209b6b2cde
Revises: 1a3acfbeabbd
Create Date: 2026-06-01 21:11:16.716219

"""
from typing import Sequence, Union

from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision: str = 'b7209b6b2cde'
down_revision: Union[str, Sequence[str], None] = '1a3acfbeabbd'
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    op.add_column(
        "qualifying_raw",
        sa.Column("race_date", sa.Date(), nullable=True)
    )
    
    op.add_column(
        "results_raw",
        sa.Column("race_date", sa.Date(), nullable=True)
    )


def downgrade() -> None:
    op.drop_column("results_raw", "race_date")
    op.drop_column("qualifying_raw", "race_date")
