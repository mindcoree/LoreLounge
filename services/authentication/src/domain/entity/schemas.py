"""
Схемы Pydantic для auth-service.

Все схемы работают с LoreLounge-ролями (Role, DesiredRole, RoleRequestStatus).
"""

from pydantic import BaseModel, EmailStr, Field, ConfigDict
from datetime import datetime
from domain.common.enums import Role, DesiredRole, RoleRequestStatus
from typing import Optional


# ── Базовая схема пользователя (используется в security.py) ─────────────────


class AuthEntitySchema(BaseModel):
    """Минимальный набор данных для создания JWT-токенов."""

    id: int
    login: str
    role: Role
    email: EmailStr


# ── Регистрация / вход ───────────────────────────────────────────────────────


class AuthEntityIn(BaseModel):
    """Данные для регистрации новой сущности."""

    email: EmailStr
    login: str = Field(min_length=3, max_length=80, description="Логин пользователя")
    password: str = Field(min_length=8, max_length=128)
    role: DesiredRole = DesiredRole.READER


class AuthEntityOut(BaseModel):
    """Данные, возвращаемые после успешной регистрации / из /me."""

    model_config = ConfigDict(from_attributes=True)

    id: int
    login: str
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
    login: str
    role: Role
    email: EmailStr


# ── Заявки на роль ───────────────────────────────────────────────────────────


class RoleRequestCreate(BaseModel):
    requested_desired_role: DesiredRole


class RoleRequestOut(BaseModel):
    model_config = ConfigDict(from_attributes=True)

    id: int
    entity_id: int
    requested_role: DesiredRole
    status: RoleRequestStatus
    created_at: Optional[datetime] = None
    updated_at: Optional[datetime] = None


class RoleRequestListOut(BaseModel):
    model_config = ConfigDict(from_attributes=True)

    total: int
    items: list[RoleRequestOut]


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
