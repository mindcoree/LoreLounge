from typing import Annotated

from sqlalchemy.orm import mapped_column
from sqlalchemy import JSON
from pydantic import Field, StringConstraints, BaseModel

TOKEN_TYPE_FIELD = "type"
ACCESS_TOKEN_TYPE = "access"
REFRESH_TOKEN_TYPE = "refresh"


"""Ключ для access-токена в cookie."""
ACCESS_TOKEN_COOKIE_KEY = "access_token"
"""Ключ для refresh-токена в cookie."""
REFRESH_TOKEN_COOKIE_KEY = "refresh_token"


JSON = Annotated[dict, mapped_column(JSON)]


login = Annotated[
    str,
    Field(
        min_length=8,
        max_length=40,
        description="Login must be between 8 and 40 characters.",
        examples=["mindcore"],
    ),
]

password = Annotated[
    str,
    StringConstraints(
        min_length=8,
        max_length=40,
        pattern=r"^[A-Za-z\d@$!%*#?&]+$",
    ),
]

