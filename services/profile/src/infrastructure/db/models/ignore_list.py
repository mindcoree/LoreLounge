from typing import TYPE_CHECKING
from uuid import UUID

from infrastructure.db.types.mixins import TimestampMix

from sqlalchemy.orm import Mapped, mapped_column, relationship
from sqlalchemy import ForeignKey, UniqueConstraint
from .base import Base


if TYPE_CHECKING:
    from .profile import Profile


class IgnoreList(TimestampMix,Base):
    __tablename__ = "ignore_lists"

    id: Mapped[int] = mapped_column(primary_key=True, autoincrement=True)

    # The user who is ignoring another user
    user_id: Mapped[UUID] = mapped_column(
        ForeignKey("profiles.user_id", ondelete="CASCADE"),
        index=True,
        nullable=False,
    )

    # The user being ignored
    ignored_user_id: Mapped[UUID] = mapped_column(
        ForeignKey("profiles.user_id", ondelete="CASCADE"),
        index=True,
        nullable=False,
    )

    # Unique constraint to prevent duplicate ignore entries for the same user pair
    __table_args__ = (
        UniqueConstraint("user_id", "ignored_user_id", name="uq_user_ignored"),
    )

    # Relationships (Links from IgnoreList to Profile)

    # profile of the person who is ignoring
    ignorer: Mapped["Profile"] = relationship(
        "Profile", 
        foreign_keys=[user_id], 
        back_populates="ignored_users_links"
    )

    # profile of the person being ignored
    ignored: Mapped["Profile"] = relationship(
        "Profile", 
        foreign_keys=[ignored_user_id], 
        back_populates="ignored_by_links"
    )