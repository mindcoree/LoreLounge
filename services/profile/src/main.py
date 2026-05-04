"""
Точка входа profile.

Запуск:
    uvicorn src.main:app --host 0.0.0.0 --port 8000 --reload
"""

import logging
from contextlib import asynccontextmanager

from fastapi import FastAPI

from config.settings import settings
from infrastructure.db.db_helper import db_helper

logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s | %(levelname)-8s | %(name)s — %(message)s",
)
logger = logging.getLogger(__name__)


# ── Lifespan ──────────────────────────────────────────────────────────────────


@asynccontextmanager
async def lifespan(app: FastAPI):
    """Управление жизненным циклом: создаём пул при старте, закрываем при остановке."""
    logger.info("🚀profile запускается…")

    yield

    logger.info("🛑 profile останавливается, закрываем пул соединений…")
    await db_helper.dispose()
 

# ── Приложение ────────────────────────────────────────────────────────────────
app = FastAPI(
    title="LoreLounge — Profile Service",
    description="Микросервис профилей для платформы LoreLounge.",
    version="0.1.0",
    lifespan=lifespan,
    # Указываем root_path /api
    root_path="/api",
    # Путь к Swagger станет /api/profile/docs (если включен)
    docs_url="/profile/docs" if settings.run.show_docs else None,
    # Настройки для "чистоты" Swagger
    swagger_ui_parameters={"defaultModelsExpandDepth": -1} 
)   



@app.get("/healthz", tags=["Infra"], summary="Проверка работоспособности сервиса")
async def health_check() -> dict:
    return {"status": "ok", "service": "profile"}
