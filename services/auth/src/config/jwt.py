"""
JWT configuration settings for auth service.
"""

from pathlib import Path
from typing import Optional, final

from pydantic import BaseModel


@final
class AuthJWT(BaseModel):
    """JWT signing and verification settings using RS256."""

    private_key: Path = Path(__file__).resolve().parents[2] / "certs" / "private_key.pem"
    public_key: Path = Path(__file__).resolve().parents[2] / "certs" / "public_key.pem"
    algorithm: str = "RS256"
    access_expire_min: int = 15
    refresh_expire_min: Optional[int] = None
    refresh_expire_days: int = 7
