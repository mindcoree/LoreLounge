from fastapi import FastAPI
from typing import Any, cast

from domain.exceptions import (
    ProfileConflictError,
    ProfileNotFoundError,
    ProfileNameTakenError,
    SelfIgnoreError,
    UserAlreadyIgnoredError,
    UserNotInIgnoreListError,
    MediaFormatError,
    MediaSizeError,
)

from .error_profile import (
    profile_conflict_handler,
    profile_not_found_handler,
    profile_name_taken_handler,
)

from .error_ignore_list import (
    self_ignore_handler,
    user_already_ignored_handler,
    user_not_in_ignore_list_handler,
)

from .error_media import (
    media_format_error_handler,
    media_size_error_handler,
)

def _register_exception_handler(app: FastAPI, exception_type: type[Exception], handler: Any) -> None:
    app.add_exception_handler(exception_type, cast(Any, handler))


def _setup_profile_exception_handlers(app: FastAPI) -> None:
    _register_exception_handler(app, ProfileConflictError, profile_conflict_handler)
    _register_exception_handler(app, ProfileNotFoundError, profile_not_found_handler)
    _register_exception_handler(app, ProfileNameTakenError, profile_name_taken_handler)


def _setup_ignore_list_exception_handlers(app: FastAPI) -> None:
    _register_exception_handler(app, SelfIgnoreError, self_ignore_handler)
    _register_exception_handler(app, UserAlreadyIgnoredError, user_already_ignored_handler)
    _register_exception_handler(app, UserNotInIgnoreListError, user_not_in_ignore_list_handler)

def _setup_media_exception_handlers(app: FastAPI) -> None:
    _register_exception_handler(app, MediaFormatError, media_format_error_handler)
    _register_exception_handler(app, MediaSizeError, media_size_error_handler)


def setup_exception_handlers(app: FastAPI) -> None:
    """Регистрирует все глобальные обработчики ошибок для приложения."""

    _setup_profile_exception_handlers(app)
    _setup_ignore_list_exception_handlers(app)
    _setup_media_exception_handlers(app)
    # В будущем сюда можно добавить хендлеры для валидации Pydantic (422 ошибки)
    # или глобальные хендлеры для 500-х ошибок с отправкой логов в Sentry.
