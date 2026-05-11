from urllib.parse import quote

from pydantic import BaseModel, Field


class RabbitmqSettings(BaseModel):
    user: str = Field(default="guest", alias="USER")
    password: str = Field(default="guest", alias="PASSWORD")
    host: str = Field(default="localhost", alias="HOST")
    port: int = Field(default=5672, alias="PORT")
    vhost: str = Field(default="/", alias="VHOST")

    # Optional full DSN override. If provided, it has priority over split fields.
    dsn: str | None = Field(default=None, alias="URL")

    @property
    def url(self) -> str:
        if self.dsn:
            return self.dsn

        encoded_user = quote(self.user, safe="")
        encoded_password = quote(self.password, safe="")

        if self.vhost in {"", "/"}:
            vhost_part = ""
        else:
            vhost_part = quote(self.vhost.lstrip("/"), safe="")

        return f"amqp://{encoded_user}:{encoded_password}@{self.host}:{self.port}/{vhost_part}"