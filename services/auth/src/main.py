import logging
from contextlib import asynccontextmanager
import uvicorn
from fastapi import FastAPI

from config.settings import settings
from infrastructure.db.db_helper import db_helper
from api.handlers import setup_exception_handlers
from api.routers import router as api_router
from infrastructure.broker.rabbitmq import broker

logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s | %(levelname)-8s | %(name)s — %(message)s",
)
logger = logging.getLogger(__name__)


@asynccontextmanager
async def lifespan(app: FastAPI):
    """Управление жизненным циклом: создаём пул при старте, закрываем при остановке."""
    logger.info("🚀 auth запускается…")
    
    # Стартуем RabbitMQ broker
    await broker.connect()
    logger.info("🐰 Соединение с RabbitMQ установлено")
    
    yield
    
    logger.info("🛑 auth останавливается, закрываем пул соединений…")
    await db_helper.dispose()
    
    logger.info("🐰 Закрываем соединение с RabbitMQ…")
    await broker.disconnect()


def create_app() -> FastAPI:
    app = FastAPI(
        title="LoreLounge — Auth Service",
        description="Микросервис аутентификации и авторизации для платформы LoreLounge.",
        version="0.1.0",
        lifespan=lifespan,
        root_path="/api",
        docs_url="/auth/docs" if settings.run.show_docs else None,
        openapi_url="/auth/openapi.json" if settings.run.show_docs else None,
        swagger_ui_parameters={"defaultModelsExpandDepth": -1},
    )

    @app.get("/healthz", tags=["Infra"], summary="Проверка работоспособности сервиса")
    async def health_check() -> dict:
        return {"status": "ok", "service": "auth"}

    app.include_router(api_router)
    setup_exception_handlers(app)
    return app


app = create_app()


if __name__ == "__main__":
    uvicorn.run(app, host=settings.run.host, port=settings.run.port)
