from fastapi import FastAPI, Request, status
from fastapi.responses import JSONResponse
from domain.common.exceptions import (
    LoreLoungeError,
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
)

def register_exception_handlers(app: FastAPI):
    # Карта соответствия: Ошибка -> Статус
    ERROR_MAP = {
        UserAlreadyExistsError: status.HTTP_409_CONFLICT,
        InvalidCredentialsError: status.HTTP_401_UNAUTHORIZED,
        TokenExpiredError: status.HTTP_401_UNAUTHORIZED,
        UserNotFoundError: status.HTTP_401_UNAUTHORIZED,
        GatewayAuthenticationRequiredError: status.HTTP_401_UNAUTHORIZED,
        PasswordsDoNotMatchError: status.HTTP_400_BAD_REQUEST,
        InvalidOrExpiredResetTokenError: status.HTTP_400_BAD_REQUEST,
        ResetTokenAlreadyUsedError: status.HTTP_400_BAD_REQUEST,
        RoleRequestAlreadyExistsError: status.HTTP_400_BAD_REQUEST,
        RoleRequestNotFoundError: status.HTTP_404_NOT_FOUND,
        RoleRequestAlreadyProcessedError: status.HTTP_400_BAD_REQUEST,
    }

    def create_handler(status_code: int):
        async def handler(request: Request, exc: LoreLoungeError):
            return JSONResponse(
                status_code=status_code, 
                content={"detail": str(exc)}
            )
        return handler

    for error_cls, code in ERROR_MAP.items():
        app.add_exception_handler(error_cls, create_handler(code))
