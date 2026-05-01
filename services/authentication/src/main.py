"""
Точка входа auth-service.

Запуск:
    uvicorn src.main:app --host 0.0.0.0 --port 8000 --reload
"""

import logging
from contextlib import asynccontextmanager

from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from starlette.middleware.base import BaseHTTPMiddleware
from starlette.requests import Request
import jwt

from core.config import settings
from core.types import ACCESS_TOKEN_COOKIE_KEY
from core import security as auth
from infrastructure.db.session import db_helper
from api.v1.auth import router as auth_router
from api.v1.roles import router as roles_router

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
    await broker.disconnect()


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

# CORS
app.add_middleware(
    CORSMiddleware,
    allow_origins=settings.cors.origins,
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# ── Auth middleware ────────────────────────────────────────────────────────────
class AccessTokenMiddleware(BaseHTTPMiddleware):
    async def dispatch(self, request: Request, call_next):
        token = request.cookies.get(ACCESS_TOKEN_COOKIE_KEY)
        if token:
            try:
                payload = await auth.decode_jwt(token)
                request.state.auth_payload = payload
            except jwt.ExpiredSignatureError:
                request.state.token_needs_refresh = True
            except jwt.InvalidTokenError:
                # не валим запрос, просто считаем неаутентифицированным
                pass
            except Exception:
                logger.exception("Ошибка валидации access token")
        return await call_next(request)

app.add_middleware(AccessTokenMiddleware)

# Роуты
app.include_router(auth_router, prefix="/api/v1", tags=["auth"])
app.include_router(roles_router, prefix="/api/v1/role-requests", tags=["role-requests"])


# ── Health-check ──────────────────────────────────────────────────────────────


@app.get("/healthz", tags=["infra"], summary="Проверка работоспособности сервиса")
async def health_check() -> dict:
    return {"status": "ok", "service": "auth-service"}
