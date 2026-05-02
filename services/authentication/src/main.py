"""
Точка входа auth-service.

Запуск:
    uvicorn src.main:app --host 0.0.0.0 --port 8000 --reload
"""

import logging
from contextlib import asynccontextmanager

from fastapi import FastAPI

from core.config import settings
from infrastructure.db.session import db_helper
from api.v1 import router_v1

logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s | %(levelname)-8s | %(name)s — %(message)s",
)
logger = logging.getLogger(__name__)


# ── Lifespan ──────────────────────────────────────────────────────────────────


@asynccontextmanager
async def lifespan(app: FastAPI):
    """Управление жизненным циклом: создаём пул при старте, закрываем при остановке."""
    logger.info("🚀 auth-service запускается…")
    
    # Стартуем RabbitMQ broker
    from infrastructure.broker.rabbitmq import broker
    await broker.connect()
    logger.info("🐰 Соединение с RabbitMQ установлено")
    
    yield
    
    logger.info("🛑 auth-service останавливается, закрываем пул соединений…")
    await db_helper.dispose()
    
    logger.info("🐰 Закрываем соединение с RabbitMQ…")
    await broker.close()


# ── Приложение ────────────────────────────────────────────────────────────────


app = FastAPI(
    title="LoreLounge — Auth Service",
    description="Микросервис аутентификации и авторизации для платформы LoreLounge.",
    version="0.1.0",
    lifespan=lifespan,
    docs_url="/api/v1/docs",
    redoc_url="/api/v1/redoc",
    openapi_url="/api/v1/openapi.json",
)

# Роуты
app.include_router(router_v1, prefix="/api/v1", tags=["v1"])


@app.get("/healthz", tags=["infra"], summary="Проверка работоспособности сервиса")
async def health_check() -> dict:
    return {"status": "ok", "service": "auth-service"}
