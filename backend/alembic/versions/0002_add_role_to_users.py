"""add role to users

Revision ID: 0002_add_role_to_users
Revises: 0001_init
Create Date: 2025-09-27
"""
from alembic import op
import sqlalchemy as sa

# revision identifiers, used by Alembic.
revision = "0002_add_role_to_users"
down_revision = "0001_init"
branch_labels = None
depends_on = None

def upgrade() -> None:
    op.add_column("users", sa.Column("role", sa.String(length=32), nullable=False, server_default="patient"))
    # после добавления можно убрать server_default, чтобы не оставался в схеме:
    op.alter_column("users", "role", server_default=None)

def downgrade() -> None:
    op.drop_column("users", "role")
