from fastapi import Depends
from typing import Annotated

from .session import SessionDep

from domain.services.auth import AuthServices
from domain.services.roles import RoleRequestService
from infrastructure.db.repositories.auth_repo import AuthSQLAlchemyRepository
from infrastructure.db.repositories.role_request_repo import RoleRequestRepository
from infrastructure.broker.rabbitmq import broker
from infrastructure.cache.redis import get_redis
from redis.asyncio import Redis


async def get_auth_service(session: SessionDep, redis: Redis = Depends(get_redis)) -> AuthServices:
    return AuthServices(
        repository=AuthSQLAlchemyRepository(session=session),
        message_broker=broker,
        redis=redis,
        role_request_repo=RoleRequestRepository(session=session),
    )


AuthServiceDep = Annotated[AuthServices, Depends(get_auth_service)]


async def get_role_request_service(session: SessionDep) -> RoleRequestService:
    return RoleRequestService(
        repo=RoleRequestRepository(session=session),
        entity_repo=AuthSQLAlchemyRepository(session=session),
    )


RoleRequestServiceDep = Annotated[RoleRequestService, Depends(get_role_request_service)]
