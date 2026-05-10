"""
Redis client for auth revoke storage.
"""

from functools import lru_cache

from redis.asyncio import Redis

from core.config import settings


@lru_cache(maxsize=1)
def get_redis() -> Redis:
    return Redis.from_url(settings.redis.url, decode_responses=True)
