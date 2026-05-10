from uuid import UUID

from pydantic import BaseModel


class AccountDeletionNotification(BaseModel):
    user_id: UUID