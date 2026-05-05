"""
Конфигурация Alembic для auth (async mode с asyncpg).

Запуск из папки services/auth/:
    ../../.venv/bin/alembic revision --autogenerate -m "init auth tables"
    ../../.venv/bin/alembic upgrade head
"""

import asyncio
import os
import sys
from logging.config import fileConfig
from pathlib import Path

from sqlalchemy import pool
from sqlalchemy.engine import Connection
from sqlalchemy.ext.asyncio import async_engine_from_config
from alembic import context

# ── 1. Добавляем src/ в PYTHONPATH ───────────────────────────────────────────
# Файл лежит в: services/auth/alembic/env.py
# src/ лежит в: services/auth/src/
SERVICE_DIR = Path(__file__).parent.parent          # services/auth/
SRC_DIR = SERVICE_DIR / "src"
PROJECT_ROOT = SERVICE_DIR.parent.parent            # LoreLounge/

sys.path.insert(0, str(SRC_DIR))

# ── 2. Загружаем .env из корня проекта ───────────────────────────────────────
# pydantic-settings ищет .env относительно CWD, но мы запускаем alembic
# из services/auth/ — поэтому грузим явно.
env_file = PROJECT_ROOT / ".env"
if env_file.exists():
    from dotenv import load_dotenv
    load_dotenv(dotenv_path=env_file, override=False)

# ── 3. Подставляем дефолтный URL для локальной разработки ────────────────────
# Если CONFIG__DB__URL не задан (например, нет .env или он пустой),
# берём переменные AUTH_DB_* и собираем URL сами.
if not os.environ.get("CONFIG__DB__URL"):
    user = os.environ.get("AUTH_DB_USER", "auth_admin")
    password = os.environ.get("AUTH_DB_PASSWORD", "auth_secret")
    db = os.environ.get("AUTH_DB_NAME", "lorelounge_auth")
    # Для локального запуска (не Docker) — localhost:5432
    os.environ["CONFIG__DB__URL"] = (
        f"postgresql+asyncpg://{user}:{password}@localhost:5432/{db}"
    )

# ── 4. Импортируем настройки и модели ────────────────────────────────────────
from core.config import settings
from infrastructure.db.base import Base
import infrastructure.db.models  # noqa: F401, F403 — чтобы alembic видел таблицы


# ─────────────────────────────────────────────────────────────────────────────

config = context.config
config.set_main_option("sqlalchemy.url", str(settings.db.url))

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