"""
ORM-модель RoleRequest — заявка на повышение роли.
"""

from uuid import UUID

from sqlalchemy import Enum as SAEnum
from sqlalchemy.dialects.postgresql import UUID as PGUUID
from sqlalchemy.orm import Mapped, mapped_column

from infrastructure.db.models.base import Base
from infrastructure.db.types.mixins import TimestampMix
from domain.enums import DesiredRole, RoleRequestStatus


class RoleRequest(Base, TimestampMix):
    """Заявка на смену роли."""

    __tablename__ = "role_requests"

    id: Mapped[int] = mapped_column(primary_key=True, autoincrement=True)
    entity_id: Mapped[UUID] = mapped_column(
        PGUUID(as_uuid=True),
        nullable=False,
        index=True,
    )
    requested_role: Mapped[DesiredRole] = mapped_column(
        SAEnum(DesiredRole, name="desired_role_enum"),
        nullable=False,
    )
    status: Mapped[RoleRequestStatus] = mapped_column(
        SAEnum(RoleRequestStatus, name="role_request_status_enum"),
        nullable=False,
        default=RoleRequestStatus.PENDING,
        server_default=RoleRequestStatus.PENDING.name,
    )
