from typing import Generic, Any, cast
from uuid import UUID
from sqlalchemy import select, update, delete
from sqlalchemy.ext.asyncio import AsyncSession

from infrastructure.db.types.model_type import ModelType


class BaseRepository(Generic[ModelType]):
    def __init__(self, model: type[ModelType], session: AsyncSession):
        self.model = model
        self.session = session

    async def get_by_id(self, id: int | UUID) -> ModelType | None:
        model_id = cast(Any, getattr(self.model, "id"))
        query = select(self.model).where(model_id == id)
        result = await self.session.execute(query)
        return result.scalar_one_or_none()

    async def create(self, **kwargs: Any) -> ModelType:
        obj = self.model(**kwargs)
        self.session.add(obj)
        await self.session.flush()
        return obj

    async def update(self, id: int | UUID, **kwargs: Any) -> ModelType | None:
        model_id = cast(Any, getattr(self.model, "id"))
        query = (
            update(self.model)
            .where(model_id == id)
            .values(**kwargs)
            .returning(self.model)
        )
        result = await self.session.execute(query)
        await self.session.flush()
        return result.scalar_one_or_none()

    async def delete(self, id: int | UUID) -> bool:
        model_id = cast(Any, getattr(self.model, "id"))
        query = delete(self.model).where(model_id == id)
        result = await self.session.execute(query)
        await self.session.flush()
        return cast(Any, result).rowcount > 0
