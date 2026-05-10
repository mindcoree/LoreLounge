"""
Domain events (messages published to RabbitMQ).
"""

from uuid import UUID

from pydantic import BaseModel, EmailStr


class PasswordResetNotification(BaseModel):
    to_email: EmailStr
    reset_link: str


class AccountDeletionNotification(BaseModel):
    user_id: UUID
