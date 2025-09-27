"""add clinic_id fk to doctor_profiles

Revision ID: c340b9509c0d
Revises: 0002_add_role_to_users
Create Date: 2025-09-27 08:34:23.803469

"""
from alembic import op
import sqlalchemy as sa

# revision identifiers, used by Alembic.
revision = 'c340b9509c0d'
down_revision = '0002_add_role_to_users'
branch_labels = None
depends_on = None

def upgrade() -> None:
    pass

def downgrade() -> None:
    pass
