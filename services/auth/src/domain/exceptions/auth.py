from uuid import UUID
from .base import DomainError


class UserAlreadyExistsError(DomainError):
    def __init__(self, email: str | None = None):
        self.email = email
        msg = f"Пользователь с email '{email}' уже существует." if email else "Пользователь с таким email уже существует."
        super().__init__(msg)


class InvalidCredentialsError(DomainError):
    def __init__(self, detail: str = "Неверный email или пароль."):
        super().__init__(detail)


class TokenExpiredError(DomainError):
    def __init__(self, detail: str = "Токен невалиден или просрочен."):
        super().__init__(detail)


class UserNotFoundError(DomainError):
    def __init__(self, identifier: UUID | str | None = None):
        self.identifier = identifier
        msg = f"Пользователь {identifier} не найден." if identifier else "Пользователь не найден."
        super().__init__(msg)


class GatewayAuthenticationRequiredError(DomainError):
    def __init__(self):
        super().__init__("Требуется аутентификация через Gateway.")
