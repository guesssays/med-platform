from alembic import op
import sqlalchemy as sa

# revision identifiers, used by Alembic.
revision = "055530e10aa2"
down_revision = "5c8e3700f2dc"

branch_labels = None
depends_on = None

def upgrade():
    # Легаси-поля могли уже быть удалены вручную — используем IF EXISTS
    op.execute("ALTER TABLE users DROP COLUMN IF EXISTS hashed_password")
    op.execute("ALTER TABLE users DROP COLUMN IF EXISTS phone")
    op.execute("ALTER TABLE users DROP COLUMN IF EXISTS is_active")
    op.execute("ALTER TABLE users DROP COLUMN IF EXISTS is_superadmin")
    op.execute("ALTER TABLE users DROP COLUMN IF EXISTS created_at")
    op.execute("ALTER TABLE users DROP COLUMN IF EXISTS role")

    # На свежей БД страхуемся: делаем уникальность email (если вдруг нет)
    with op.get_context().autocommit_block():
        op.execute("""
        DO $$
        BEGIN
            IF NOT EXISTS (
              SELECT 1 FROM pg_indexes WHERE indexname = 'users_email_key'
            ) THEN
              ALTER TABLE users ADD CONSTRAINT users_email_key UNIQUE (email);
            END IF;
        END$$;
        """)

def downgrade():
    # Возврат (минимальный) — создадим обратно столбцы как NULLABLE без данных
    op.add_column("users", sa.Column("phone", sa.String(length=32), nullable=True))
    op.add_column("users", sa.Column("is_active", sa.Boolean(), nullable=True))
    op.add_column("users", sa.Column("is_superadmin", sa.Boolean(), nullable=True))
    op.add_column("users", sa.Column("created_at", sa.DateTime(), nullable=True))
    op.add_column("users", sa.Column("role", sa.String(length=32), nullable=True))
    op.add_column("users", sa.Column("hashed_password", sa.String(length=255), nullable=True))
