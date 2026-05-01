"""
Управление подключениями к PostgreSQL через SQLAlchemy asyncpg.

DataBaseHelper инкапсулирует engine + session_factory.
Используй SessionDep как FastAPI dependency для получения AsyncSession.
"""

from asyncio import current_task
from typing import AsyncGenerator, Annotated, Any

from fastapi import Depends
from sqlalchemy.ext.asyncio import (
    AsyncEngine,
    AsyncSession,
    async_scoped_session,
    async_sessionmaker,
    create_async_engine,
)

from core.config import settings


class DataBaseHelper:
    """
    Помощник для работы с async PostgreSQL.

    Создаёт движок (engine) и фабрику сессий (session_factory) один раз
    при старте приложения. Движок закрывается через dispose() в lifespan.
    """

    def __init__(
        self,
        url: str,
        echo: bool = False,
        echo_pool: bool = False,
        pool_size: int = 20,
        max_overflow: int = 10,
    ) -> None:
        self.engine: AsyncEngine = create_async_engine(
            url=url,
            echo=echo,
            echo_pool=echo_pool,
            pool_size=pool_size,
            max_overflow=max_overflow,
            # Переподключение при разрыве соединения
            pool_pre_ping=True,
            pool_recycle=3600,
        )
        self.session_factory: async_sessionmaker[AsyncSession] = async_sessionmaker(
            bind=self.engine,
            autoflush=False,
            expire_on_commit=False,
            class_=AsyncSession,
        )

    async def dispose(self) -> None:
        """Закрыть пул соединений при остановке приложения."""
        await self.engine.dispose()

    async def session_getter(self) -> AsyncGenerator[AsyncSession, None]:
        """
        FastAPI dependency: выдаёт AsyncSession на время запроса.

        Сессия автоматически закрывается при выходе из context manager,
        даже если возникло исключение.
        """
        async with self.session_factory() as session:
            yield session


db_helper = DataBaseHelper(
    url=str(settings.db.url),
    echo=settings.db.echo,
    echo_pool=settings.db.echo_pool,
    pool_size=settings.db.pool_size,
    max_overflow=settings.db.max_overflow,
)

# ── FastAPI dependency type alias ─────────────────────────────────────────────

SessionDep = Annotated[AsyncSession, Depends(db_helper.session_getter)]


# ── Scoped session (для Celery / фоновых задач) ───────────────────────────────


def get_scoped_session() -> async_scoped_session[AsyncSession]:
    """Создаёт сессию, привязанную к текущему asyncio-таску."""
    return async_scoped_session(
        session_factory=db_helper.session_factory,
        scopefunc=current_task,
    )


async def scoped_session_dependency() -> (
    AsyncGenerator[async_scoped_session[AsyncSession | Any], Any]
):
    """FastAPI dependency для scoped-сессии (используй в фоновых задачах)."""
    session = get_scoped_session()
    yield session
    await session.remove()
