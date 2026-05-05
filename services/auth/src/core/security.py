"""
Утилиты безопасности: JWT (RS256) + bcrypt.

Все CPU-bound операции (bcrypt, jwt.encode/decode) выполняются в thread pool
через asyncio.to_thread — event loop не блокируется.

⚠️  Параметры-по-умолчанию (private_key, algorithm и т.д.) вычисляются
    при первом реальном вызове функции, а НЕ при импорте модуля, чтобы
    избежать ошибок «settings не загружены».
"""

import asyncio
import logging
from datetime import datetime, timezone, timedelta
from functools import lru_cache
from uuid import uuid4

import bcrypt
import jwt
import base64
from cryptography.hazmat.primitives import serialization
from fastapi import Response

from core.config import settings
from core.types import TOKEN_TYPE_FIELD, ACCESS_TOKEN_TYPE, REFRESH_TOKEN_TYPE, JTI_FIELD
from domain.entity.schemas import AuthEntitySchema

logger = logging.getLogger(__name__)

# Cookie secure flag: False для dev, True для prod (HTTPS)
COOKIE_SECURE = False


# ── Ключи ────────────────────────────────────────────────────────────────────


@lru_cache(maxsize=1)
def get_private_key() -> str:
    """Читает и кэширует приватный RSA-ключ для подписи JWT."""
    return settings.auth.private_key.read_text()


@lru_cache(maxsize=1)
def get_public_key() -> str:
    """Читает и кэширует публичный RSA-ключ для верификации JWT."""
    return settings.auth.public_key.read_text()


@lru_cache(maxsize=1)
def get_jwk_params() -> dict:
    """Извлекает RSA-параметры (n, e) для JWKS."""
    public_key_pem = get_public_key()
    public_key = serialization.load_pem_public_key(public_key_pem.encode("utf-8"))
    numbers = public_key.public_numbers()

    def b64url(n: int) -> str:
        size = (n.bit_length() + 7) // 8
        b = n.to_bytes(size, byteorder='big')
        return base64.urlsafe_b64encode(b).decode('utf-8').rstrip('=')

    return {
        "kty": "RSA",
        "alg": "RS256",
        "use": "sig",
        "kid": "lorelounge-key",
        "n": b64url(numbers.n),
        "e": b64url(numbers.e)
    }


# ── JWT encode / decode ──────────────────────────────────────────────────────


async def encode_jwt(
    payload: dict,
    expire_minute: int | None = None,
    expire_timedelta: timedelta | None = None,
) -> str:
    """
    Создаёт подписанный JWT.

    Срок жизни определяется:
      1. expire_timedelta — если передан явно;
      2. expire_minute — если передан;
      3. settings.auth.access_expire_min — дефолт.
    """
    private_key = get_private_key()
    algorithm = settings.auth.algorithm

    now = datetime.now(timezone.utc)
    if expire_timedelta is not None:
        expire = now + expire_timedelta
    elif expire_minute is not None:
        expire = now + timedelta(minutes=expire_minute)
    else:
        expire = now + timedelta(minutes=settings.auth.access_expire_min)

    to_encode = payload.copy()
    to_encode.update(exp=int(expire.timestamp()), iat=int(now.timestamp()))

    return await asyncio.to_thread(
        jwt.encode,
        payload=to_encode,
        key=private_key,
        algorithm=algorithm,
        headers={"kid": "lorelounge-key"},
    )


async def decode_jwt(token: str) -> dict:
    """
    Декодирует и верифицирует JWT.

    Raises jwt.exceptions.InvalidTokenError при невалидном/просроченном токене.
    """
    public_key = get_public_key()
    algorithm = settings.auth.algorithm

    return await asyncio.to_thread(
        jwt.decode,
        jwt=token,
        key=public_key,
        algorithms=[algorithm],
    )


# ── Пароли ───────────────────────────────────────────────────────────────────


async def hash_password(password: str) -> str:
    """Хеширует пароль через bcrypt в thread pool (CPU-bound)."""
    password_bytes = password.encode("utf-8")
    salt = bcrypt.gensalt()
    hashed: bytes = await asyncio.to_thread(bcrypt.hashpw, password_bytes, salt)
    return hashed.decode("utf-8")


async def verify_password(password: str, hashed_password: str | bytes) -> bool:
    """
    Проверяет пароль против bcrypt-хеша.

    Принимает хеш как str или bytes — оба случая корректно обрабатываются.
    """
    password_bytes = password.encode("utf-8")
    if isinstance(hashed_password, str):
        hashed_bytes = hashed_password.encode("utf-8")
    else:
        hashed_bytes = hashed_password

    return await asyncio.to_thread(
        bcrypt.checkpw,
        password=password_bytes,
        hashed_password=hashed_bytes,
    )


# ── Построение токенов ───────────────────────────────────────────────────────


def create_payload(auth_payload: AuthEntitySchema) -> dict:
    """Формирует стандартный payload для access-токена."""
    return {
        "sub": str(auth_payload.id),
        "email": auth_payload.email,
        "role": auth_payload.role,
    }


async def _create_jwt(
    token_data: dict,
    token_type: str,
    expire_minute: int | None = None,
    expire_timedelta: timedelta | None = None,
) -> str:
    payload = {TOKEN_TYPE_FIELD: token_type}
    payload.update(token_data)
    return await encode_jwt(
        payload=payload,
        expire_minute=expire_minute,
        expire_timedelta=expire_timedelta,
    )


async def create_access_token(auth_info: AuthEntitySchema) -> str:
    """Создаёт access-токен (RS256, срок = access_expire_min)."""
    payload = create_payload(auth_payload=auth_info)
    return await _create_jwt(
        token_data=payload,
        token_type=ACCESS_TOKEN_TYPE,
        expire_minute=settings.auth.access_expire_min,
    )


async def create_refresh_token(auth_info: AuthEntitySchema) -> str:
    """Создаёт refresh-токен (RS256, срок = refresh_expire_days)."""
    payload = {
        "sub": str(auth_info.id),
        JTI_FIELD: str(uuid4()),
    }
    if settings.auth.refresh_expire_min is not None:
        return await _create_jwt(
            token_data=payload,
            token_type=REFRESH_TOKEN_TYPE,
            expire_timedelta=timedelta(minutes=settings.auth.refresh_expire_min),
        )
    return await _create_jwt(
        token_data=payload,
        token_type=REFRESH_TOKEN_TYPE,
        expire_timedelta=timedelta(days=settings.auth.refresh_expire_days),
    )


# ── Cookie ───────────────────────────────────────────────────────────────────


async def set_token_cookie(
    response: Response,
    key: str,
    value: str,
    max_age: int,
    httponly: bool = True,
    samesite: str = "lax",
    secure: bool = COOKIE_SECURE,
) -> None:
    """Устанавливает JWT в http-only cookie."""
    response.set_cookie(
        key=key,
        value=value,
        max_age=max_age,
        httponly=httponly,
        samesite=samesite,
        secure=secure,
    )
