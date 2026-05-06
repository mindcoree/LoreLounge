from fastapi import FastAPI
from typing import Any, cast


from src.domain.exceptions import (
    ProfileNotFoundError,
    ProfileAlreadyExistsError,
    SelfIgnoreError,
    UserAlreadyIgnoredError,
    UserNotInIgnoreListError,
)

from .error_profile import (
    profile_not_found_handler,
    profile_already_exists_handler
)

from .error_ignore_list import (
    self_ignore_handler,
    user_already_ignored_handler,
    user_not_in_ignore_list_handler,
)

def setup_exception_handlers(app: FastAPI) -> None:
    """Регистрирует все глобальные обработчики ошибок для приложения."""

    app.add_exception_handler(ProfileNotFoundError, profile_not_found_handler) # type: ignore
    app.add_exception_handler(ProfileAlreadyExistsError, profile_already_exists_handler) # type: ignore
    app.add_exception_handler(SelfIgnoreError, self_ignore_handler) # type: ignore
    app.add_exception_handler(UserAlreadyIgnoredError, user_already_ignored_handler) # type: ignore
    app.add_exception_handler(UserNotInIgnoreListError, user_not_in_ignore_list_handler) # type: ignore
    # В будущем сюда можно добавить хендлеры для валидации Pydantic (422 ошибки)
    # или глобальные хендлеры для 500-х ошибок с отправкой логов в Sentry.
