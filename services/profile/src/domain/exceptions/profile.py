from uuid import UUID
from .base import DomainError

class ProfileNotFoundError(DomainError):
    def __init__(self, identifier: UUID | str):
        self.identifier = identifier
        super().__init__(f"Profile {identifier} not found.")

class ProfileAlreadyExistsError(DomainError):
    def __init__(self, user_id: UUID):
        self.user_id = user_id
        super().__init__(f"Profile for user {user_id} already exists.")
