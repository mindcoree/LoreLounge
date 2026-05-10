"""
Схемы Pydantic для заявок на смену роли.
"""

from datetime import datetime
from uuid import UUID
from pydantic import BaseModel, ConfigDict
from domain.enums import DesiredRole, RoleRequestStatus
from typing import Optional


class RoleRequestCreate(BaseModel):
    requested_desired_role: DesiredRole


class RoleRequestOut(BaseModel):
    model_config = ConfigDict(from_attributes=True)

    id: int
    entity_id: UUID
    requested_role: DesiredRole
    status: RoleRequestStatus
    created_at: Optional[datetime] = None
    updated_at: Optional[datetime] = None


class RoleRequestListOut(BaseModel):
    model_config = ConfigDict(from_attributes=True)

    total: int
    items: list[RoleRequestOut]
