from alembic import op
import sqlalchemy as sa

# revision identifiers, used by Alembic.
revision = "959bac8f101e"
down_revision = "055530e10aa2"
branch_labels = None
depends_on = None


ENUM_NAME = "userrole"
ENUM_VALUES = ("admin", "doctor", "patient")


def upgrade() -> None:
    # 1) Создаём тип, если его нет
    bind = op.get_bind()
    insp = sa.inspect(bind)

    # Проверим, существует ли уже enum с таким именем
    enum_exists = bind.exec_driver_sql(
        "SELECT 1 FROM pg_type WHERE typname = %(name)s", {"name": ENUM_NAME}
    ).scalar() is not None

    if not enum_exists:
        op.execute(
            sa.text(
                f"CREATE TYPE {ENUM_NAME} AS ENUM ({', '.join([f'''{v!r}''' for v in ENUM_VALUES])})"
            )
        )
    else:
        # 2) Гарантируем наличие всех значений
        for v in ENUM_VALUES:
            op.execute(
                sa.text(
                    f"""
                    DO $$
                    BEGIN
                        IF NOT EXISTS (
                            SELECT 1
                            FROM pg_enum e
                            JOIN pg_type t ON e.enumtypid = t.oid
                            WHERE t.typname = :enum_name AND e.enumlabel = :label
                        ) THEN
                            ALTER TYPE {ENUM_NAME} ADD VALUE :label;
                        END IF;
                    END $$;
                    """
                ).bindparams(sa.bindparam("enum_name", ENUM_NAME), sa.bindparam("label", v))
            )

    # 3) Добавляем колонку с явным кастом дефолта к enum
    op.add_column(
        "users",
        sa.Column(
            "role",
            sa.dialects.postgresql.ENUM(*ENUM_VALUES, name=ENUM_NAME, create_type=False),
            nullable=False,
            server_default=sa.text(f"'patient'::{ENUM_NAME}"),
        ),
    )


def downgrade() -> None:
    # Удаляем колонку
    op.drop_column("users", "role")
    # Тип оставляем (безопаснее для последующих миграций);
    # если точно надо удалить тип, раскомментируйте:
    # op.execute(sa.text(f"DROP TYPE IF EXISTS {ENUM_NAME}"))
