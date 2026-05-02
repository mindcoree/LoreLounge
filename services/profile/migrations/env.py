import asyncio
import os
import sys
from logging.config import fileConfig
from pathlib import Path

from sqlalchemy import pool
from sqlalchemy.ext.asyncio import async_engine_from_config
from sqlalchemy.engine import Connection
from alembic import context




# ── 1. Добавляем src/ в PYTHONPATH ───────────────────────────────────────────
# Файл лежит в: services/profile/migrations/env.py
# src/ лежит в: services/profile/src/
SERVICE_DIR = Path(__file__).parent.parent          # services/profile/
SRC_DIR = SERVICE_DIR / "src"
PROJECT_ROOT = SERVICE_DIR.parent.parent            # LoreLounge/

sys.path.insert(0, str(SRC_DIR))

# ── 2. Загружаем .env из корня проекта ───────────────────────────────────────
# pydantic-settings ищет .env относительно CWD, но мы запускаем alembic
# из services/profile/ — поэтому грузим явно.
env_file = PROJECT_ROOT / ".env"
if env_file.exists():
    from dotenv import load_dotenv
    load_dotenv(dotenv_path=env_file, override=False)




# ── 3. Подставляем дефолтный URL для локальной разработки ────────────────────
# Если CONFIG__DB__URL не задан (например, нет .env или он пустой),
# берём переменные PROFILE_DB_* и собираем URL сами.
if not os.environ.get("CONFIG__DB__URL"):
    user = os.environ.get("PROFILE_DB_USER", "profile_admin")
    password = os.environ.get("PROFILE_DB_PASSWORD", "profile_secret")
    db = os.environ.get("PROFILE_DB_NAME", "lorelounge_profile")
    # Для локального запуска (не Docker) — localhost:5432
    os.environ["CONFIG__DB__URL"] = (
        f"postgresql+asyncpg://{user}:{password}@localhost:5432/{db}"
    )





# ── 4. Импортируем настройки и модели ────────────────────────────────────────
# from core.config import settings
# from src.infrastructure.db.models import Base  # noqa: F401, F403 — чтобы alembic видел таблицы
# from src.infrastructure.db.models import Base  # noqa: F401, F403 — чтобы alembic видел таблицы
# ─────────────────────────────────────────────────────────────────────────────

# this is the Alembic Config object, which provides
# access to the values within the .ini file in use.

config = context.config
# config.set_main_option("sqlalchemy.url", str(settings.db.url))



# Interpret the config file for Python logging.
# This line sets up loggers basically.
if config.config_file_name is not None:
    fileConfig(config.config_file_name)

# add your model's MetaData object here
# for 'autogenerate' support
# from myapp import mymodel
# target_metadata = mymodel.Base.metadata
target_metadata = None

# other values from the config, defined by the needs of env.py,
# can be acquired:
# my_important_option = config.get_main_option("my_important_option")
# ... etc.


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


async def run_async_migrations() -> None:
    connectable = async_engine_from_config(
        config.get_section(config.config_ini_section, {}),
        prefix="sqlalchemy.",
        poolclass=pool.NullPool,
    )
    async with connectable.connect() as connection:
        await connection.run_sync(do_run_migrations)
    await connectable.dispose()


def run_migrations_online() -> None:
    asyncio.run(run_async_migrations())


# ─────────────────────────────────────────────────────────────────────────────

if context.is_offline_mode():
    run_migrations_offline()
else:
    run_migrations_online()