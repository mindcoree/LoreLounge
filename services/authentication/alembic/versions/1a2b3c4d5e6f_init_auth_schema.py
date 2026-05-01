"""init auth schema with uuid

Revision ID: 1a2b3c4d5e6f
Revises:
Create Date: 2026-05-01 18:45:00.000000

"""
from typing import Sequence, Union

from alembic import op
import sqlalchemy as sa
from sqlalchemy.dialects import postgresql


# revision identifiers, used by Alembic.
revision: str = "1a2b3c4d5e6f"
down_revision: Union[str, Sequence[str], None] = None
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    op.create_table(
        "auth_entities",
        sa.Column("id", postgresql.UUID(as_uuid=True), server_default=sa.text("uuid_generate_v4()"), nullable=False),
        sa.Column("email", sa.String(length=255), nullable=False),
        sa.Column("login", sa.String(length=80), nullable=False),
        sa.Column("hash_password", sa.String(length=255), nullable=False),
        sa.Column(
            "role",
            sa.Enum("ADMIN", "READER", "AUTHOR", "TRANSLATOR", "MODERATOR", name="role_enum"),
            server_default="READER",
            nullable=False,
        ),
        sa.Column("created_at", sa.DateTime(timezone=True), server_default=sa.text("now()"), nullable=False),
        sa.Column("updated_at", sa.DateTime(timezone=True), server_default=sa.text("now()"), nullable=False),
        sa.PrimaryKeyConstraint("id", name=op.f("pk_auth_entities")),
    )
    op.create_index(op.f("ix_auth_entities_email"), "auth_entities", ["email"], unique=True)
    op.create_index(op.f("ix_auth_entities_login"), "auth_entities", ["login"], unique=True)

    op.create_table(
        "role_requests",
        sa.Column("id", sa.Integer(), autoincrement=True, nullable=False),
        sa.Column("entity_id", postgresql.UUID(as_uuid=True), nullable=False),
        sa.Column(
            "requested_role",
            sa.Enum("READER", "AUTHOR", "TRANSLATOR", "MODERATOR", name="desired_role_enum"),
            nullable=False,
        ),
        sa.Column(
            "status",
            sa.Enum("PENDING", "APPROVED", "REJECTED", name="role_request_status_enum"),
            server_default="PENDING",
            nullable=False,
        ),
        sa.Column("created_at", sa.DateTime(timezone=True), server_default=sa.text("now()"), nullable=False),
        sa.Column("updated_at", sa.DateTime(timezone=True), server_default=sa.text("now()"), nullable=False),
        sa.PrimaryKeyConstraint("id", name=op.f("pk_role_requests")),
        sa.ForeignKeyConstraint(["entity_id"], ["auth_entities.id"], name=op.f("fk_role_requests_entity_id_auth_entities")),
    )
    op.create_index(op.f("ix_role_requests_entity_id"), "role_requests", ["entity_id"], unique=False)

    op.create_table(
        "password_reset_tokens",
        sa.Column("id", sa.Integer(), autoincrement=True, nullable=False),
        sa.Column("entity_id", postgresql.UUID(as_uuid=True), nullable=False),
        sa.Column("token_hash", sa.String(length=64), nullable=False),
        sa.Column("expires_at", sa.DateTime(timezone=True), nullable=False),
        sa.Column("used", sa.Boolean(), server_default=sa.text("false"), nullable=False),
        sa.PrimaryKeyConstraint("id", name=op.f("pk_password_reset_tokens")),
        sa.ForeignKeyConstraint(["entity_id"], ["auth_entities.id"], name=op.f("fk_password_reset_tokens_entity_id_auth_entities")),
    )
    op.create_index(op.f("ix_password_reset_tokens_entity_id"), "password_reset_tokens", ["entity_id"], unique=False)
    op.create_index(op.f("ix_password_reset_tokens_token_hash"), "password_reset_tokens", ["token_hash"], unique=True)


def downgrade() -> None:
    op.drop_index(op.f("ix_password_reset_tokens_token_hash"), table_name="password_reset_tokens")
    op.drop_index(op.f("ix_password_reset_tokens_entity_id"), table_name="password_reset_tokens")
    op.drop_table("password_reset_tokens")
    op.drop_index(op.f("ix_role_requests_entity_id"), table_name="role_requests")
    op.drop_table("role_requests")
    op.drop_index(op.f("ix_auth_entities_login"), table_name="auth_entities")
    op.drop_index(op.f("ix_auth_entities_email"), table_name="auth_entities")
    op.drop_table("auth_entities")
    op.execute("DROP TYPE IF EXISTS role_request_status_enum")
    op.execute("DROP TYPE IF EXISTS desired_role_enum")
    op.execute("DROP TYPE IF EXISTS role_enum")
