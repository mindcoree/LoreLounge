"""
Схемы Pydantic для auth.

Все схемы работают с LoreLounge-ролями (Role, DesiredRole, RoleRequestStatus).
"""

from datetime import datetime
from uuid import UUID

from pydantic import BaseModel, EmailStr, Field, ConfigDict
from domain.common.enums import Role, DesiredRole, RoleRequestStatus
from typing import Optional


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

    email: str
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





# ── Сброс пароля ─────────────────────────────────────────────────────────────


class PasswordResetRequest(BaseModel):
    email: EmailStr


class PasswordResetConfirm(BaseModel):
    token: str
    new_password: str = Field(min_length=8, max_length=128)
    repeat_password: str = Field(min_length=8, max_length=128)


class PasswordResetResponse(BaseModel):
    detail: str


# ── RabbitMQ ─────────────────────────────────────────────────────────────────


class PasswordResetNotification(BaseModel):
    to_email: EmailStr
    reset_link: str


class AccountDeletionNotification(BaseModel):
    user_id: UUID

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
