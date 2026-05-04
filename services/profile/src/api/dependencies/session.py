from typing import Annotated
from fastapi import Depends
from sqlalchemy.ext.asyncio import AsyncSession

# Импортируем наш helper из слоя инфраструктуры
from infrastructure.db.db_helper import db_helper
 
# Создаем FastAPI зависимость
SessionDep = Annotated[AsyncSession, Depends(db_helper.get_session)]