from fastapi import FastAPI
from typing import Any, cast

from domain.exceptions import (
    UserAlreadyExistsError,
    InvalidCredentialsError,
    TokenExpiredError,
    UserNotFoundError,
    GatewayAuthenticationRequiredError,
    PasswordsDoNotMatchError,
    InvalidOrExpiredResetTokenError,
    ResetTokenAlreadyUsedError,
    RoleRequestAlreadyExistsError,
    RoleRequestNotFoundError,
    RoleRequestAlreadyProcessedError,
    InvalidCurrentPasswordError,
)

from .error_auth import (
    user_already_exists_handler,
    invalid_credentials_handler,
    token_expired_handler,
    user_not_found_handler,
    gateway_auth_required_handler,
)

from .error_password import (
    passwords_do_not_match_handler,
    invalid_or_expired_reset_token_handler,
    reset_token_already_used_handler,
    invalid_current_password_handler,
)

from fastapi.exceptions import RequestValidationError

from .error_roles import (
    role_request_already_exists_handler,
    role_request_not_found_handler,
    role_request_already_processed_handler,
)

from .error_validation import validation_exception_handler

def _register_exception_handler(app: FastAPI, exception_type: type[Exception], handler: Any) -> None:
    app.add_exception_handler(exception_type, cast(Any, handler))


def _setup_auth_exception_handlers(app: FastAPI) -> None:
    _register_exception_handler(app, UserAlreadyExistsError, user_already_exists_handler)
    _register_exception_handler(app, InvalidCredentialsError, invalid_credentials_handler)
    _register_exception_handler(app, TokenExpiredError, token_expired_handler)
    _register_exception_handler(app, UserNotFoundError, user_not_found_handler)
    _register_exception_handler(app, GatewayAuthenticationRequiredError, gateway_auth_required_handler)


def _setup_password_exception_handlers(app: FastAPI) -> None:
    _register_exception_handler(app, PasswordsDoNotMatchError, passwords_do_not_match_handler)
    _register_exception_handler(app, InvalidOrExpiredResetTokenError, invalid_or_expired_reset_token_handler)
    _register_exception_handler(app, ResetTokenAlreadyUsedError, reset_token_already_used_handler)
    _register_exception_handler(app, InvalidCurrentPasswordError, invalid_current_password_handler)


def _setup_roles_exception_handlers(app: FastAPI) -> None:
    _register_exception_handler(app, RoleRequestAlreadyExistsError, role_request_already_exists_handler)
    _register_exception_handler(app, RoleRequestNotFoundError, role_request_not_found_handler)
    _register_exception_handler(app, RoleRequestAlreadyProcessedError, role_request_already_processed_handler)


def _setup_validation_exception_handlers(app: FastAPI) -> None:
    _register_exception_handler(app, RequestValidationError, validation_exception_handler)


def setup_exception_handlers(app: FastAPI) -> None:
    """Регистрирует все глобальные обработчики ошибок для приложения."""
    _setup_auth_exception_handlers(app)
    _setup_password_exception_handlers(app)
    _setup_roles_exception_handlers(app)
    _setup_validation_exception_handlers(app)
