from asyncio import current_task
from typing import AsyncGenerator

from sqlalchemy.ext.asyncio import (
    AsyncEngine,
    AsyncSession,
    async_scoped_session,
    async_sessionmaker,
    create_async_engine,
)
from config.settings import settings


class DataBaseHelper:
    def __init__(self, url: str, pool_size: int = 20, max_overflow: int = 10):
        self.engine: AsyncEngine = create_async_engine(
            url=url,
            pool_size=pool_size,
            max_overflow=max_overflow,
            pool_pre_ping=True,
        )
        self.session_factory: async_sessionmaker[AsyncSession] = async_sessionmaker(
            bind=self.engine,
            autoflush=False,
            expire_on_commit=False,
        )

    async def dispose(self) -> None:
        await self.engine.dispose()

    async def session_getter(self) -> AsyncGenerator[AsyncSession, None]:
        """Генерирует сессию (пока без привязки к FastAPI)"""
        async with self.session_factory() as session:
            yield session


# Создаем глобальный объект-помощник
db_helper = DataBaseHelper(
    url=str(settings.db.url),
    pool_size=settings.db.pool_size,
    max_overflow=settings.db.max_overflow,
)


# Для фоновых задач (RabbitMQ)
def get_scoped_session() -> async_scoped_session[AsyncSession]:
    return async_scoped_session(
        session_factory=db_helper.session_factory,
        scopefunc=current_task,
    )
