"""add name/avatar to users, goals and reflections tables

Revision ID: g3h4i5j6k7l8
Revises: f1a2b3c4d5e6
Create Date: 2026-05-11 00:00:00.000000

"""
from alembic import op
import sqlalchemy as sa

revision = 'g3h4i5j6k7l8'
down_revision = 'f1a2b3c4d5e6'
branch_labels = None
depends_on = None


def upgrade() -> None:
    # Add name and avatar_url to users
    op.add_column('users', sa.Column('name', sa.String(255), nullable=True))
    op.add_column('users', sa.Column('avatar_url', sa.Text, nullable=True))

    # Goals table
    op.create_table(
        'goals',
        sa.Column('id', sa.dialects.postgresql.UUID(as_uuid=True), primary_key=True),
        sa.Column('user_id', sa.dialects.postgresql.UUID(as_uuid=True),
                  sa.ForeignKey('users.id', ondelete='CASCADE'), nullable=False),
        sa.Column('name', sa.String(100), nullable=False),
        sa.Column('target_minutes', sa.Integer, nullable=False),
        sa.Column('current_minutes', sa.Integer, nullable=False, server_default='0'),
        sa.Column('period', sa.String(20), nullable=False, server_default='weekly'),
        sa.Column('color', sa.String(20), nullable=True),
        sa.Column('created_at', sa.DateTime(timezone=True),
                  server_default=sa.func.now(), nullable=False),
    )
    op.create_index('ix_goals_user_id', 'goals', ['user_id'])

    # Reflections table
    op.create_table(
        'reflections',
        sa.Column('id', sa.dialects.postgresql.UUID(as_uuid=True), primary_key=True),
        sa.Column('user_id', sa.dialects.postgresql.UUID(as_uuid=True),
                  sa.ForeignKey('users.id', ondelete='CASCADE'), nullable=False),
        sa.Column('date', sa.Date, nullable=False),
        sa.Column('content', sa.Text, nullable=False),
        sa.Column('created_at', sa.DateTime(timezone=True),
                  server_default=sa.func.now(), nullable=False),
        sa.Column('updated_at', sa.DateTime(timezone=True),
                  server_default=sa.func.now(), nullable=False),
        sa.UniqueConstraint('user_id', 'date', name='uq_reflection_user_date'),
    )
    op.create_index('ix_reflections_user_id', 'reflections', ['user_id'])


def downgrade() -> None:
    op.drop_table('reflections')
    op.drop_table('goals')
    op.drop_column('users', 'avatar_url')
    op.drop_column('users', 'name')
