from __future__ import annotations
from logging.config import fileConfig
from sqlalchemy import engine_from_config, pool
from alembic import context

# >>> гарантируем, что каталог /app (где лежит пакет app) в sys.path
import os, sys
BASE_DIR = os.path.abspath(os.path.join(os.path.dirname(__file__), ".."))  # /app
if BASE_DIR not in sys.path:
    sys.path.insert(0, BASE_DIR)
# <<<

# Alembic Config object
config = context.config

# logging
if config.config_file_name is not None:
    fileConfig(config.config_file_name)

# sqlalchemy url из .env (если есть)
db_url = os.getenv("DATABASE_URL")
if db_url:
    config.set_main_option("sqlalchemy.url", db_url)

# импортируем Base из отдельного файла, чтобы избежать циклов
from app.db.base_class import Base  # noqa: E402
# и подсвечиваем модели (побочный импорт собирает все модели в metadata)
import app.db.base  # noqa: F401

target_metadata = Base.metadata

def run_migrations_offline() -> None:
    url = config.get_main_option("sqlalchemy.url")
    context.configure(url=url, target_metadata=target_metadata, literal_binds=True, compare_type=True)
    with context.begin_transaction():
        context.run_migrations()

def run_migrations_online() -> None:
    connectable = engine_from_config(
        config.get_section(config.config_ini_section, {}),
        prefix="sqlalchemy.",
        poolclass=pool.NullPool,
    )
    with connectable.connect() as connection:
        context.configure(connection=connection, target_metadata=target_metadata, compare_type=True)
        with context.begin_transaction():
            context.run_migrations()

if context.is_offline_mode():
    run_migrations_offline()
else:
    run_migrations_online()
