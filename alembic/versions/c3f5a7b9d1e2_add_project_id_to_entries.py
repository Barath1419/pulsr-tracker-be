"""add_project_id_to_entries

Revision ID: c3f5a7b9d1e2
Revises: a6313a0c59d8
Create Date: 2026-04-10

"""
from typing import Sequence, Union

from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision: str = 'c3f5a7b9d1e2'
down_revision: Union[str, None] = 'a6313a0c59d8'
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    op.add_column(
        "entries",
        sa.Column("project_id", sa.UUID(), nullable=True),
    )
    op.create_foreign_key(
        "fk_entry_project_id",
        "entries", "projects",
        ["project_id"], ["id"],
        ondelete="SET NULL",
    )


def downgrade() -> None:
    op.drop_constraint("fk_entry_project_id", "entries", type_="foreignkey")
    op.drop_column("entries", "project_id")
