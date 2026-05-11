import logging 
from contextlib import asynccontextmanager
import uvicorn
from fastapi import FastAPI

from config.settings import settings


from infrastructure.db.db_helper import db_helper


logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s | %(levelname)-8s | %(name)s — %(message)s",
)
logger = logging.getLogger(__name__)


@asynccontextmanager
async def lifespan(app: FastAPI):
    """Lifecycle management: initialize resources on startup, clean up on shutdown."""
    logger.info("🚀 Content service is starting...")
    # register_broker_subscribers()
    # await broker.start()

    yield

    logger.info("🛑 Content service is shutting down, closing connection pool...")
    # await broker.stop()
    await db_helper.dispose()


def create_app() -> FastAPI:
    app = FastAPI(
        title="LoreLounge — Content Service",
        description="Content microservice for the LoreLounge platform.",
        version="0.1.0",
        lifespan=lifespan,
        root_path="/api",
        docs_url="/content/docs" if settings.run.show_docs else None,
        openapi_url="/content/openapi.json" if settings.run.show_docs else None,
        swagger_ui_parameters={"defaultModelsExpandDepth": -1},
    )

    @app.get("/healthz", tags=["Infra"], summary="Service health check")
    async def health_check() -> dict:
        return {"status": "ok", "service": "content"}

    # app.include_router(api_router)
    # setup_exception_handlers(app)
    return app


app = create_app()


if __name__ == "__main__":
    uvicorn.run(app, host=settings.run.host, port=settings.run.port)