from uuid import UUID

from sqlalchemy.exc import IntegrityError

from domain.exceptions import (
    ProfileConflictError,
    ProfileNameTakenError,
    ProfileAlreadyExistsError,
)


def map_profile_integrity_error(
    exc: IntegrityError,
    *,
    user_id: UUID | None = None,
    name: str | None = None,
) -> Exception:
    error_text = str(exc).lower()
    if "profiles_user_id_key" in error_text or "(user_id)" in error_text:
        if user_id is not None:
            return ProfileAlreadyExistsError(user_id)
    if "profiles_name_key" in error_text or "(name)" in error_text:
        return ProfileNameTakenError(name or "")
    return ProfileConflictError()
