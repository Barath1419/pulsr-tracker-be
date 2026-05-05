"""add google_id to users and make password_hash nullable

Revision ID: f1a2b3c4d5e6
Revises: e1f3a5c7d9b0
Create Date: 2026-05-05 00:00:00.000000

"""
from alembic import op
import sqlalchemy as sa

revision = 'f1a2b3c4d5e6'
down_revision = 'e1f3a5c7d9b0'
branch_labels = None
depends_on = None


def upgrade() -> None:
    op.add_column('users', sa.Column('google_id', sa.String(255), nullable=True))
    op.create_unique_constraint('uq_users_google_id', 'users', ['google_id'])
    op.create_index('ix_users_google_id', 'users', ['google_id'])
    op.alter_column('users', 'password_hash', nullable=True)


def downgrade() -> None:
    op.alter_column('users', 'password_hash', nullable=False)
    op.drop_index('ix_users_google_id', table_name='users')
    op.drop_constraint('uq_users_google_id', 'users', type_='unique')
    op.drop_column('users', 'google_id')
