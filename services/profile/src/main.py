import logging
from contextlib import asynccontextmanager
import uvicorn
from fastapi import FastAPI

from config.settings import settings
from infrastructure.db.db_helper import db_helper
from api.handlers import setup_exception_handlers
from api.routers import router as api_router

logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s | %(levelname)-8s | %(name)s — %(message)s",
)
logger = logging.getLogger(__name__)


@asynccontextmanager
async def lifespan(app: FastAPI):
    """Lifecycle management: initialize resources on startup, clean up on shutdown."""
    logger.info("🚀 Profile service is starting...")

    yield

    logger.info("🛑 Profile service is shutting down, closing connection pool...")
    await db_helper.dispose()


def create_app() -> FastAPI:
    app = FastAPI(
        title="LoreLounge — Profile Service",
        description="Profile microservice for the LoreLounge platform.",
        version="0.1.0",
        lifespan=lifespan,
        docs_url="/profile/docs" if settings.run.show_docs else None,
        swagger_ui_parameters={"defaultModelsExpandDepth": -1},
    )

    @app.get("/healthz", tags=["Infra"], summary="Service health check")
    async def health_check() -> dict:
        return {"status": "ok", "service": "profile"}

    app.include_router(api_router)
    setup_exception_handlers(app)
    return app


app = create_app()


if __name__ == "__main__":
    uvicorn.run(app, host=settings.run.host, port=settings.run.port)