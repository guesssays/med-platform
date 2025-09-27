"""init manual

Revision ID: 0001_init
Revises: 
Create Date: 2025-09-27

"""
from alembic import op
import sqlalchemy as sa
from sqlalchemy.dialects import postgresql

# revision identifiers, used by Alembic.
revision = '0001_init'
down_revision = None
branch_labels = None
depends_on = None


def upgrade() -> None:
    # users
    op.create_table(
        'users',
        sa.Column('id', sa.Integer(), primary_key=True),
        sa.Column('email', sa.String(length=255), nullable=False),
        sa.Column('phone', sa.String(length=32), nullable=True),
        sa.Column('hashed_password', sa.String(length=255), nullable=False),
        sa.Column('is_active', sa.Boolean(), nullable=False, server_default=sa.text('true')),
        sa.Column('is_superadmin', sa.Boolean(), nullable=False, server_default=sa.text('false')),
        sa.Column('created_at', sa.DateTime(), nullable=False, server_default=sa.text('CURRENT_TIMESTAMP')),
        sa.UniqueConstraint('email'),
        sa.UniqueConstraint('phone')
    )
    op.create_index('ix_users_email', 'users', ['email'], unique=False)

    # clinics
    op.create_table(
        'clinics',
        sa.Column('id', sa.Integer(), primary_key=True),
        sa.Column('name', sa.String(length=255), nullable=False),
        sa.Column('slug', sa.String(length=255), nullable=False),
        sa.Column('owner_id', sa.Integer(), nullable=True),
        sa.ForeignKeyConstraint(['owner_id'], ['users.id']),
        sa.UniqueConstraint('name'),
        sa.UniqueConstraint('slug')
    )
    op.create_index('ix_clinics_slug', 'clinics', ['slug'], unique=False)

    # doctor_profiles
    op.create_table(
        'doctor_profiles',
        sa.Column('id', sa.Integer(), primary_key=True),
        sa.Column('user_id', sa.Integer(), nullable=False, unique=True),
        sa.Column('clinic_id', sa.Integer(), nullable=True),
        sa.Column('specialty', sa.String(length=255), nullable=True),
        sa.ForeignKeyConstraint(['user_id'], ['users.id']),
        sa.ForeignKeyConstraint(['clinic_id'], ['clinics.id']),
    )

    # patient_profiles
    op.create_table(
        'patient_profiles',
        sa.Column('id', sa.Integer(), primary_key=True),
        sa.Column('user_id', sa.Integer(), nullable=False, unique=True),
        sa.ForeignKeyConstraint(['user_id'], ['users.id']),
    )

    # appointments
    op.create_table(
        'appointments',
        sa.Column('id', sa.Integer(), primary_key=True),
        sa.Column('doctor_id', sa.Integer(), nullable=False),
        sa.Column('patient_id', sa.Integer(), nullable=False),
        sa.Column('starts_at', sa.DateTime(), nullable=False),
        sa.Column('ends_at', sa.DateTime(), nullable=False),
        sa.Column('status', sa.String(length=32), nullable=False, server_default='scheduled'),
        sa.ForeignKeyConstraint(['doctor_id'], ['doctor_profiles.id']),
        sa.ForeignKeyConstraint(['patient_id'], ['patient_profiles.id']),
    )

    # content_items
    op.create_table(
        'content_items',
        sa.Column('id', sa.Integer(), primary_key=True),
        sa.Column('author_doctor_id', sa.Integer(), nullable=False),
        sa.Column('title', sa.String(length=255), nullable=False),
        sa.Column('kind', sa.String(length=32), nullable=False),
        sa.Column('body', sa.Text(), nullable=True),
        sa.Column('r2_key', sa.String(length=512), nullable=True),
        sa.Column('created_at', sa.DateTime(), nullable=False, server_default=sa.text('CURRENT_TIMESTAMP')),
        sa.ForeignKeyConstraint(['author_doctor_id'], ['doctor_profiles.id']),
    )

    # subscriptions
    op.create_table(
        'subscriptions',
        sa.Column('id', sa.Integer(), primary_key=True),
        sa.Column('patient_id', sa.Integer(), nullable=False),
        sa.Column('doctor_id', sa.Integer(), nullable=False),
        sa.Column('is_active', sa.Boolean(), nullable=False, server_default=sa.text('true')),
        sa.Column('started_at', sa.DateTime(), nullable=False, server_default=sa.text('CURRENT_TIMESTAMP')),
        sa.Column('expires_at', sa.DateTime(), nullable=True),
        sa.ForeignKeyConstraint(['patient_id'], ['patient_profiles.id']),
        sa.ForeignKeyConstraint(['doctor_id'], ['doctor_profiles.id']),
    )

    # payments
    op.create_table(
        'payments',
        sa.Column('id', sa.Integer(), primary_key=True),
        sa.Column('user_id', sa.Integer(), nullable=False),
        sa.Column('provider', sa.String(length=64), nullable=False),
        sa.Column('amount', sa.Numeric(12, 2), nullable=False),
        sa.Column('currency', sa.String(length=8), nullable=False, server_default='UZS'),
        sa.Column('status', sa.String(length=32), nullable=False, server_default='pending'),
        sa.Column('created_at', sa.DateTime(), nullable=False, server_default=sa.text('CURRENT_TIMESTAMP')),
        sa.ForeignKeyConstraint(['user_id'], ['users.id']),
    )
def downgrade() -> None:
    op.drop_table('payments')
    op.drop_table('subscriptions')
    op.drop_table('content_items')
    op.drop_table('appointments')
    op.drop_table('patient_profiles')
    op.drop_table('doctor_profiles')
    op.drop_index('ix_clinics_slug', table_name='clinics')
    op.drop_table('clinics')
    op.drop_index('ix_users_email', table_name='users')
    op.drop_table('users')
