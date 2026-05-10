"""
ORM-модель AuthEntity — пользователь платформы LoreLounge.
"""

from uuid import UUID

from sqlalchemy import String, Enum as SAEnum, text
from sqlalchemy.dialects.postgresql import UUID as PGUUID
from sqlalchemy.orm import Mapped, mapped_column

from infrastructure.db.models.base import Base
from infrastructure.db.types.mixins import TimestampMix
from domain.enums import Role


class AuthEntity(Base, TimestampMix):
    """Пользователь платформы."""

    __tablename__ = "auth_entities"

    id: Mapped[UUID] = mapped_column(
        PGUUID(as_uuid=True),
        primary_key=True,
        server_default=text("uuid_generate_v4()"),
    )
    email: Mapped[str] = mapped_column(String(255), unique=True, nullable=False, index=True)
    hash_password: Mapped[str] = mapped_column(String(255), nullable=False)
    role: Mapped[Role] = mapped_column(
        SAEnum(Role, name="role_enum"),
        nullable=False,
        default=Role.READER,
        server_default=Role.READER.name,
    )
