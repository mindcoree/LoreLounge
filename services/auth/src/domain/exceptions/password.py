from .base import DomainError


class PasswordsDoNotMatchError(DomainError):
    def __init__(self):
        super().__init__("Пароли не совпадают.")


class InvalidOrExpiredResetTokenError(DomainError):
    def __init__(self):
        super().__init__("Некорректный или просроченный токен сброса пароля.")


class ResetTokenAlreadyUsedError(DomainError):
    def __init__(self):
        super().__init__("Токен сброса пароля уже использован.")


class InvalidCurrentPasswordError(DomainError):
    def __init__(self):
        super().__init__("Текущий пароль указан неверно.")
