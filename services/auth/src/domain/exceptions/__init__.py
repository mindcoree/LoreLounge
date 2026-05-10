from .base import LoreLoungeError, DomainError
from .auth import (
    UserAlreadyExistsError,
    InvalidCredentialsError,
    TokenExpiredError,
    UserNotFoundError,
    GatewayAuthenticationRequiredError,
)
from .password import (
    PasswordsDoNotMatchError,
    InvalidOrExpiredResetTokenError,
    ResetTokenAlreadyUsedError,
    InvalidCurrentPasswordError,
)
from .roles import (
    RoleRequestAlreadyExistsError,
    RoleRequestNotFoundError,
    RoleRequestAlreadyProcessedError,
)

__all__ = [
    "LoreLoungeError",
    "DomainError",
    "UserAlreadyExistsError",
    "InvalidCredentialsError",
    "TokenExpiredError",
    "UserNotFoundError",
    "GatewayAuthenticationRequiredError",
    "PasswordsDoNotMatchError",
    "InvalidOrExpiredResetTokenError",
    "ResetTokenAlreadyUsedError",
    "RoleRequestAlreadyExistsError",
    "RoleRequestNotFoundError",
    "RoleRequestAlreadyProcessedError",
    "InvalidCurrentPasswordError",
]
