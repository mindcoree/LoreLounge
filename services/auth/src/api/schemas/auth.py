"""
Схемы Pydantic для auth.
"""

from datetime import datetime
from uuid import UUID

from pydantic import BaseModel, EmailStr, Field, ConfigDict
from domain.enums import Role, DesiredRole


# ── Базовая схема пользователя (используется в security.py) ─────────────────


class AuthEntitySchema(BaseModel):
    """Минимальный набор данных для создания JWT-токенов."""

    id: UUID
    role: Role
    email: EmailStr


# ── Регистрация / вход ───────────────────────────────────────────────────────


class AuthEntityIn(BaseModel):
    """Данные для регистрации новой сущности."""

    email: EmailStr
    password: str = Field(min_length=8, max_length=128)
    role: DesiredRole = DesiredRole.READER


class AuthEntityOut(BaseModel):
    """Данные, возвращаемые после успешной регистрации / из /me."""

    model_config = ConfigDict(from_attributes=True)

    id: UUID
    email: EmailStr
    role: Role


class AuthCredentials(BaseModel):
    """Учётные данные для входа в систему."""

    email: EmailStr
    password: str


# ── Токены ───────────────────────────────────────────────────────────────────


class TokenInfo(BaseModel):
    """Пара access / refresh токенов."""

    access: str
    refresh: str


class AccessTokenPayload(BaseModel):
    """Payload access-токена, извлекаемый из JWT."""

    sub: str
    role: Role
    email: EmailStr


# ── Domain models ────────────────────────────────────────────────────────────


class DomainAuthEntity(BaseModel):
    id: UUID
    email: str
    role: Role
    hash_password: str


class DomainPasswordResetToken(BaseModel):
    id: int
    entity_id: UUID
    token_hash: str
    expires_at: datetime
    used: bool
