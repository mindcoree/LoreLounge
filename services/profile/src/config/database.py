from pathlib import Path
from typing import cast, final

from pydantic import BaseModel, Field, PostgresDsn, computed_field


@final
class DatabaseSettings(BaseModel):
    """
    Database configuration settings.

    Attributes:
        postgres_user (str): PostgreSQL username.
        postgres_password (str): PostgreSQL password.
        postgres_server (str): PostgreSQL server host.
        postgres_port (int): PostgreSQL server port.
        postgres_db (str): PostgreSQL database name.
    """

    postgres_user: str = Field("profile_admin", alias="POSTGRES_USER")
    postgres_password: str = Field("profile_secret", alias="POSTGRES_PASSWORD")
    postgres_server: str = Field("localhost", alias="POSTGRES_SERVER")
    postgres_port: int = Field(5432, alias="POSTGRES_PORT")
    postgres_db: str = Field("lorelounge_profile", alias="POSTGRES_DB")

    @computed_field
    @property
    def url(self) -> PostgresDsn:
        """
        Constructs the PostgreSQL database URL.

        Returns:
            PostgresDsn: The constructed database URL.
        """
        return PostgresDsn.build(
            scheme="postgresql+asyncpg",
            username=self.postgres_user,
            password=self.postgres_password,
            host=self.postgres_server,
            port=self.postgres_port,
            path=self.postgres_db,
        )

    @computed_field
    @property
    def sqlalchemy_database_uri(self) -> PostgresDsn:
        """
        Returns the SQLAlchemy compatible database URI.

        Returns:
            PostgresDsn: The SQLAlchemy database URI.
        """
        return cast(PostgresDsn, self.url)

    echo: bool = False
    echo_pool: bool = False
    pool_size: int = 20
    max_overflow: int = 10
    naming_convention: dict[str, str] = Field(
        default_factory=lambda: {
            "ix": "ix_%(column_0_label)s",
            "uq": "uq_%(table_name)s_%(column_0_name)s",
            "ck": "ck_%(table_name)s_%(constraint_name)s",
            "fk": "fk_%(table_name)s_%(column_0_name)s_%(referred_table_name)s",
            "pk": "pk_%(table_name)s",
        }
    )