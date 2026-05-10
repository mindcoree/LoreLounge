"""
Схемы Pydantic для сброса пароля.
"""

from pydantic import BaseModel, EmailStr, Field


class PasswordResetRequest(BaseModel):
    email: EmailStr


class PasswordResetConfirm(BaseModel):
    token: str
    new_password: str = Field(min_length=8, max_length=128)
    repeat_password: str = Field(min_length=8, max_length=128)


class PasswordResetResponse(BaseModel):
    detail: str


class PasswordChangeRequest(BaseModel):
    current_password: str
    new_password: str = Field(min_length=8, max_length=128)
    repeat_password: str = Field(min_length=8, max_length=128)


class PasswordChangeResponse(BaseModel):
    detail: str
