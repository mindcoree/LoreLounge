"""
ORM-модели для auth-service.

AuthEntity    — пользователь платформы LoreLounge.
RoleRequest   — заявка на повышение роли.
"""

from datetime import datetime
from uuid import UUID

from sqlalchemy import String, Enum as SAEnum, Boolean, DateTime, ForeignKey, text
from sqlalchemy.dialects.postgresql import UUID as PGUUID
from sqlalchemy.orm import Mapped, mapped_column

from infrastructure.db.base import Base
from infrastructure.db.mixins import TimestampMix
from domain.common.enums import Role, DesiredRole, RoleRequestStatus


class AuthEntity(Base, TimestampMix):
    """Пользователь платформы."""

    __tablename__ = "auth_entities"

    id: Mapped[UUID] = mapped_column(
        PGUUID(as_uuid=True),
        primary_key=True,
        server_default=text("uuid_generate_v4()"),
    )
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


class PasswordResetToken(Base):
    """Одноразовый токен для сброса пароля."""

    __tablename__ = "password_reset_tokens"

    id: Mapped[int] = mapped_column(primary_key=True, autoincrement=True)
    entity_id: Mapped[UUID] = mapped_column(
        PGUUID(as_uuid=True),
        ForeignKey("auth_entities.id"),
        index=True,
    )
    token_hash: Mapped[str] = mapped_column(String(64), unique=True, nullable=False, index=True)
    expires_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), nullable=False)
    used: Mapped[bool] = mapped_column(Boolean, nullable=False, default=False, server_default="false")
