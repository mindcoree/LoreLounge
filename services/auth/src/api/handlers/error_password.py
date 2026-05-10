from fastapi import Request, status
from fastapi.responses import JSONResponse

from domain.exceptions import (
    PasswordsDoNotMatchError,
    InvalidOrExpiredResetTokenError,
    ResetTokenAlreadyUsedError,
    InvalidCurrentPasswordError,
)


async def passwords_do_not_match_handler(
    request: Request,
    exc: PasswordsDoNotMatchError,
) -> JSONResponse:
    return JSONResponse(
        status_code=status.HTTP_400_BAD_REQUEST,
        content={"detail": str(exc)},
    )


async def invalid_or_expired_reset_token_handler(
    request: Request,
    exc: InvalidOrExpiredResetTokenError,
) -> JSONResponse:
    return JSONResponse(
        status_code=status.HTTP_400_BAD_REQUEST,
        content={"detail": str(exc)},
    )


async def reset_token_already_used_handler(
    request: Request,
    exc: ResetTokenAlreadyUsedError,
) -> JSONResponse:
    return JSONResponse(
        status_code=status.HTTP_400_BAD_REQUEST,
        content={"detail": str(exc)},
    )


async def invalid_current_password_handler(
    request: Request,
    exc: InvalidCurrentPasswordError,
) -> JSONResponse:
    return JSONResponse(
        status_code=status.HTTP_400_BAD_REQUEST,
        content={"detail": str(exc)},
    )
