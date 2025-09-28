"""sync userrole enum to lowercase values

Revision ID: 202409_sync_role_lower
Revises: 959bac8f101e
Create Date: 2024-09-01 12:00:00.000000
"""
from alembic import op
import sqlalchemy as sa

revision = "202409_sync_role_lower"
down_revision = "959bac8f101e"
branch_labels = None
depends_on = None

revision = "202409_sync_role_lower"   # <= короче 32
down_revision = "959bac8f101e"
branch_labels = None
depends_on = None



def upgrade():
    # 1) новый тип с нужными (нижний регистр) значениями
    op.execute("CREATE TYPE userrole_new AS ENUM ('admin', 'doctor', 'patient');")

    # 2) снять дефолт с колонки, чтобы не держал ссылку на старый тип
    op.execute("ALTER TABLE users ALTER COLUMN role DROP DEFAULT;")

    # 3) привести имеющиеся значения к нижнему регистру и поменять тип
    op.execute(
        """
        ALTER TABLE users
          ALTER COLUMN role TYPE userrole_new
          USING lower(role::text)::userrole_new;
        """
    )

    # 4) убрать старый тип и переименовать новый в canonical имя
    op.execute("DROP TYPE userrole;")
    op.execute("ALTER TYPE userrole_new RENAME TO userrole;")

    # 5) задать новый дефолт уже на обновленный тип
    op.execute("ALTER TABLE users ALTER COLUMN role SET DEFAULT 'patient'::userrole;")


def downgrade():
    # Обратная операция: вернуть верхний регистр значений

    # 1) вернуть "верхнерегистровый" тип
    op.execute("CREATE TYPE userrole_old AS ENUM ('ADMIN', 'DOCTOR', 'PATIENT');")

    # 2) снять дефолт
    op.execute("ALTER TABLE users ALTER COLUMN role DROP DEFAULT;")

    # 3) привести значения к верхнему регистру и поменять тип
    op.execute(
        """
        ALTER TABLE users
          ALTER COLUMN role TYPE userrole_old
          USING upper(role::text)::userrole_old;
        """
    )

    # 4) удалить текущий тип и вернуть старое имя
    op.execute("DROP TYPE userrole;")
    op.execute("ALTER TYPE userrole_old RENAME TO userrole;")

    # 5) вернуть дефолт
    op.execute("ALTER TABLE users ALTER COLUMN role SET DEFAULT 'PATIENT'::userrole;")

