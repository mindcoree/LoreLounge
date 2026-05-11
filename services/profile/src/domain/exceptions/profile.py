from uuid import UUID
from .base import DomainError

class ProfileNotFoundError(DomainError):
    def __init__(self, identifier: UUID | str):
        self.identifier = identifier
        super().__init__(f"Profile {identifier} not found.")

class ProfileNameTakenError(DomainError):
    def __init__(self, name: str):
        self.name = name
        super().__init__(f"Profile name '{name}' is already taken.")


class ProfileConflictError(DomainError):
    def __init__(self):
        super().__init__("Profile conflict.")


class ProfileRepositoryInvariantError(DomainError):
    def __init__(self):
        super().__init__("Profile repository invariant violated.")


class ProfileAlreadyExistsError(DomainError):
    def __init__(self, identifier: UUID):
        self.identifier = identifier
        super().__init__(f"Profile for user {identifier} already exists.")
