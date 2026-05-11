from typing import Annotated
from fastapi import Depends
from sqlalchemy.ext.asyncio import AsyncSession

from infrastructure.db.db_helper import db_helper

SessionDep = Annotated[AsyncSession, Depends(db_helper.session_getter)]

