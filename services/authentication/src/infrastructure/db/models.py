"""
ORM-модели для auth-service.

AuthEntity    — пользователь платформы LoreLounge.
RoleRequest   — заявка на повышение роли.
"""

from sqlalchemy import String, Enum as SAEnum
from sqlalchemy.orm import Mapped, mapped_column

from infrastructure.db.base import Base
from infrastructure.db.mixins import TimestampMix
from domain.common.enums import Role, DesiredRole, RoleRequestStatus


class AuthEntity(Base, TimestampMix):
    """Пользователь платформы."""

    __tablename__ = "auth_entities"

    id: Mapped[int] = mapped_column(primary_key=True, autoincrement=True)
    email: Mapped[str] = mapped_column(String(255), unique=True, nullable=False, index=True)
    login: Mapped[str] = mapped_column(String(80), unique=True, nullable=False, index=True)
    hash_password: Mapped[str] = mapped_column(String(255), nullable=False)
    role: Mapped[Role] = mapped_column(
        SAEnum(Role, name="role_enum"),
        nullable=False,
        default=Role.READER,
        server_default=Role.READER.name,
    )


class RoleRequest(Base, TimestampMix):
    """Заявка на смену роли."""

    __tablename__ = "role_requests"

    id: Mapped[int] = mapped_column(primary_key=True, autoincrement=True)
    entity_id: Mapped[int] = mapped_column(nullable=False, index=True)
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
