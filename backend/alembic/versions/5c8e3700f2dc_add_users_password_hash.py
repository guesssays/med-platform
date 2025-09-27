"""add users.password_hash

Revision ID: 5c8e3700f2dc
Revises: c340b9509c0d
Create Date: 2025-09-27
"""
from alembic import op
import sqlalchemy as sa

# IDs из шапки файла оставь те, что у тебя (Revision ID = текущий, Revises = предыдущий)
revision = '5c8e3700f2dc'
down_revision = 'c340b9509c0d'
branch_labels = None
depends_on = None

def upgrade():
    # добавляем NOT NULL колонку в уже существующую таблицу
    op.add_column(
        'users',
        sa.Column('password_hash', sa.String(), nullable=False, server_default='')
    )
    # убираем дефолт, чтобы модель/DDL совпадали
    op.alter_column('users', 'password_hash', server_default=None)

def downgrade():
    op.drop_column('users', 'password_hash')
