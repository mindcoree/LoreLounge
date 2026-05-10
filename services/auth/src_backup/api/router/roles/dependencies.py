from typing import Annotated
from fastapi import Depends

from domain.role_requests.repository import RoleRequestRepository
from domain.role_requests.services import RoleRequestService
from infrastructure.db.session import SessionDep
from infrastructure.db.repositories.auth_repo import AuthSQLAlchemyRepository

async def get_role_request_service(session: SessionDep) -> RoleRequestService:
    return RoleRequestService(
        repo=RoleRequestRepository(session=session),
        entity_repo=AuthSQLAlchemyRepository(session=session),
    )

RoleRequestServiceDep = Annotated[RoleRequestService, Depends(get_role_request_service)]
