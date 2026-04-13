"""add_category_to_entries

Revision ID: d2e4f6a8b0c1
Revises: c3f5a7b9d1e2
Create Date: 2026-04-10

"""
from typing import Sequence, Union

from alembic import op
import sqlalchemy as sa


revision: str = 'd2e4f6a8b0c1'
down_revision: Union[str, None] = 'c3f5a7b9d1e2'
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    op.add_column(
        "entries",
        sa.Column("category", sa.String(50), nullable=True),
    )


def downgrade() -> None:
    op.drop_column("entries", "category")
