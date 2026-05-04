"""
Точка входа auth.

Запуск:
    uvicorn src.main:app --host 0.0.0.0 --port 8000 --reload
"""

import logging
from contextlib import asynccontextmanager

from fastapi import FastAPI
import uvicorn
from core.config import settings
from infrastructure.db.session import db_helper
from api.router import auth_router
from api.exception_handlers import register_exception_handlers

logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s | %(levelname)-8s | %(name)s — %(message)s",
)
logger = logging.getLogger(__name__)


# ── Lifespan ──────────────────────────────────────────────────────────────────


@asynccontextmanager
async def lifespan(app: FastAPI):
    """Управление жизненным циклом: создаём пул при старте, закрываем при остановке."""
    logger.info("🚀 auth запускается…")
    
    # Стартуем RabbitMQ broker
    from infrastructure.broker.rabbitmq import broker
    await broker.connect()
    logger.info("🐰 Соединение с RabbitMQ установлено")
    
    yield
    
    logger.info("🛑 auth останавливается, закрываем пул соединений…")
    await db_helper.dispose()
    
    logger.info("🐰 Закрываем соединение с RabbitMQ…")
    await broker.close()


# ── Приложение ────────────────────────────────────────────────────────────────
app = FastAPI(
    title="LoreLounge — Auth Service",
    description="Микросервис аутентификации и авторизации для платформы LoreLounge.",
    version="0.1.0",
    lifespan=lifespan,
    # Указываем root_path /api
    root_path="/api",
    # Путь к Swagger станет /api/auth/docs (если включен)
    docs_url="/auth/docs" if settings.run.show_docs else None,
    # OpenAPI JSON (если включен)
    openapi_url="/auth/openapi.json" if settings.run.show_docs else None,
    # Настройки для "чистоты" Swagger
    swagger_ui_parameters={"defaultModelsExpandDepth": -1} 
)   

# ❗ Подключаем всё под префиксом /auth
app.include_router(auth_router, prefix="/auth") 

# Обработчики исключений
register_exception_handlers(app)

@app.get("/healthz", tags=["Infra"], summary="Проверка работоспособности сервиса")
async def health_check() -> dict:
    return {"status": "ok", "service": "auth"}

if __name__ == "__main__":
    uvicorn.run(
        "main:app",
        host=settings.run.host,
        port=settings.run.port,
    )