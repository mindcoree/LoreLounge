from fastapi import FastAPI
# from domain.exceptions import ProfileNotFoundError, InvalidBioError
# from .domain_errors import profile_not_found_handler, invalid_bio_handler

def setup_exception_handlers(app: FastAPI) -> None:
    """Функция, которая привязывает все ошибки к FastAPI приложению"""

    # app.add_exception_handler(ProfileNotFoundError, profile_not_found_handler)
    # app.add_exception_handler(InvalidBioError, invalid_bio_handler)
    # Сюда же потом добавишь обработчики для Pydantic