"""add_categories_activities

Revision ID: e1f3a5c7d9b0
Revises: d2e4f6a8b0c1
Create Date: 2026-04-10

"""
from typing import Sequence, Union

from alembic import op
import sqlalchemy as sa


revision: str = 'e1f3a5c7d9b0'
down_revision: Union[str, None] = 'd2e4f6a8b0c1'
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    # categories table
    op.create_table(
        "categories",
        sa.Column("id", sa.UUID(), nullable=False),
        sa.Column("user_id", sa.UUID(), nullable=False),
        sa.Column("name", sa.String(255), nullable=False),
        sa.Column("type", sa.String(50), nullable=False, server_default="custom"),
        sa.Column("created_at", sa.DateTime(timezone=True), nullable=False),
        sa.PrimaryKeyConstraint("id"),
    )
    op.create_index("ix_categories_user_id", "categories", ["user_id"])

    # activities table
    op.create_table(
        "activities",
        sa.Column("id", sa.UUID(), nullable=False),
        sa.Column("user_id", sa.UUID(), nullable=False),
        sa.Column("category_id", sa.UUID(), nullable=False),
        sa.Column("project_id", sa.UUID(), nullable=True),
        sa.Column("name", sa.String(255), nullable=False),
        sa.Column("description", sa.Text(), nullable=True),
        sa.Column("type", sa.String(50), nullable=False, server_default="task"),
        sa.ForeignKeyConstraint(["category_id"], ["categories.id"], ondelete="CASCADE"),
        sa.ForeignKeyConstraint(["project_id"], ["projects.id"], ondelete="SET NULL"),
        sa.PrimaryKeyConstraint("id"),
    )
    op.create_index("ix_activities_user_id", "activities", ["user_id"])

    # add category_id to projects (nullable — existing rows stay intact)
    op.add_column("projects", sa.Column("category_id", sa.UUID(), nullable=True))
    op.create_foreign_key(
        "fk_project_category_id", "projects", "categories",
        ["category_id"], ["id"], ondelete="SET NULL",
    )

    # add activity_id to entries (nullable)
    op.add_column("entries", sa.Column("activity_id", sa.UUID(), nullable=True))
    op.create_foreign_key(
        "fk_entry_activity_id", "entries", "activities",
        ["activity_id"], ["id"], ondelete="SET NULL",
    )


def downgrade() -> None:
    op.drop_constraint("fk_entry_activity_id", "entries", type_="foreignkey")
    op.drop_column("entries", "activity_id")

    op.drop_constraint("fk_project_category_id", "projects", type_="foreignkey")
    op.drop_column("projects", "category_id")

    op.drop_index("ix_activities_user_id", table_name="activities")
    op.drop_table("activities")

    op.drop_index("ix_categories_user_id", table_name="categories")
    op.drop_table("categories")
