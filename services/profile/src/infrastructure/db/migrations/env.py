import sys
from logging.config import fileConfig
from pathlib import Path

from sqlalchemy import pool
from sqlalchemy.engine import Connection

from alembic import context


# ── 1. Добавляем src/ в PYTHONPATH ───────────────────────────────────────────
# Файл лежит в: services/profile/src/infrastructure/db/migrations/env.py
# src/ лежит в: services/profile/src/
MIGRATIONS_DIR = Path(__file__).parent            # migrations/
DB_DIR = MIGRATIONS_DIR.parent                    # db/
INFRA_DIR = DB_DIR.parent                         # infrastructure/
SRC_DIR = INFRA_DIR.parent                        # src/
SERVICE_DIR = SRC_DIR.parent                      # profile/
PROJECT_ROOT = SERVICE_DIR.parent                 # LoreLounge/

sys.path.insert(0, str(SRC_DIR))

# ── 2. Загружаем .env из корня проекта ───────────────────────────────────────
# pydantic-settings ищет .env относительно CWD, но мы запускаем alembic
# из services/profile/ — поэтому грузим явно.
env_file = PROJECT_ROOT / ".env"
if env_file.exists():
    from dotenv import load_dotenv
    load_dotenv(dotenv_path=env_file, override=False)

from config.settings import settings 
from infrastructure.db.models.base import Base
from infrastructure.db.models.profile import Profile
from infrastructure.db.models.ignore_list import IgnoreList



config = context.config

# Конвертируем async URL в sync для Alembic
db_url = str(settings.db.url).replace("postgresql+asyncpg://", "postgresql://")
config.set_main_option("sqlalchemy.url", db_url)


if config.config_file_name is not None:
    fileConfig(config.config_file_name)


target_metadata = Base.metadata

# ── Offline mode ──────────────────────────────────────────────────────────────


def run_migrations_offline() -> None:
    """Запуск миграций без создания Engine (только URL)."""
    url = config.get_main_option("sqlalchemy.url")
    context.configure(
        url=url,
        target_metadata=target_metadata,
        literal_binds=True,
        dialect_opts={"paramstyle": "named"},
        compare_type=True,
        compare_server_default=True,
    )
    with context.begin_transaction():
        context.run_migrations()


# ── Online mode ───────────────────────────────────────────────────────────────


def do_run_migrations(connection: Connection) -> None:
    context.configure(
        connection=connection,
        target_metadata=target_metadata,
        compare_type=True,
        compare_server_default=True,
    )
    with context.begin_transaction():
        context.run_migrations()


def run_migrations_online() -> None:
    from sqlalchemy import create_engine
    
    connectable = create_engine(
        config.get_main_option("sqlalchemy.url"),
        poolclass=pool.NullPool,
    )
    with connectable.connect() as connection:
        do_run_migrations(connection)


# ─────────────────────────────────────────────────────────────────────────────

if context.is_offline_mode():
    run_migrations_offline()
else:
    run_migrations_online()