class LoreLoungeError(Exception):
    """Базовое исключение для всего проекта."""
    def __init__(self, message: str):
        self.message = message
        super().__init__(self.message)

class DomainError(LoreLoungeError):
    """Базовое исключение для домена."""
    pass

class UserAlreadyExistsError(DomainError):
    """Пользователь с таким email или логином уже существует."""
    pass

class InvalidCredentialsError(DomainError):
    """Неверный email или пароль."""
    pass

class TokenExpiredError(DomainError):
    """Токен невалиден или просрочен."""
    pass

class UserNotFoundError(DomainError):
    """Пользователь не найден."""
    pass

class GatewayAuthenticationRequiredError(DomainError):
    """Требуется аутентификация через Gateway."""
    pass

class PasswordsDoNotMatchError(DomainError):
    """Пароли не совпадают."""
    pass

class InvalidOrExpiredResetTokenError(DomainError):
    """Некорректный или просроченный токен сброса пароля."""
    pass

class ResetTokenAlreadyUsedError(DomainError):
    """Токен сброса пароля уже использован."""
    pass

class RoleRequestAlreadyExistsError(DomainError):
    """Активная заявка на роль уже существует."""
    pass

class RoleRequestNotFoundError(DomainError):
    """Заявка на роль не найдена."""
    pass

class RoleRequestAlreadyProcessedError(DomainError):
    """Заявка на роль уже обработана."""
    pass
