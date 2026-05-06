from uuid import UUID
from .base import DomainError

class SelfIgnoreError(DomainError):
    def __init__(self):
        super().__init__("You cannot add yourself to the ignore list.")


class SelfIgnoreWithUserIdError(SelfIgnoreError):
    def __init__(self, user_id: UUID):
        self.user_id = user_id
        super().__init__()

class UserAlreadyIgnoredError(DomainError):
    def __init__(self, target_user_id: UUID):
        self.target_user_id = target_user_id
        super().__init__(f"User {target_user_id} is already in your ignore list.")

class UserNotInIgnoreListError(DomainError):
    def __init__(self, target_user_id: UUID):
        self.target_user_id = target_user_id
        super().__init__(f"User {target_user_id} is not in your ignore list.")
        