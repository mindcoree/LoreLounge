from typing import TypeVar

from infrastructure.db.models.base import Base

ModelType = TypeVar("ModelType", bound=Base)
