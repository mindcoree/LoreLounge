from typing import TYPE_CHECKING
from ..types.mixins import TimestampMix
from sqlalchemy.orm import Mapped, mapped_column, relationship
from sqlalchemy import String,Text
from .base import Base
from uuid import UUID

if TYPE_CHECKING:
    from .ignore_list import IgnoreList

class Profile(TimestampMix,Base):
    __tablename__ = "profiles"

    id: Mapped[int] = mapped_column(primary_key=True,autoincrement=True)
    user_id: Mapped[UUID] = mapped_column(unique=True,nullable=False)
    name: Mapped[str] = mapped_column(String(100),unique=True,index=True,nullable=False)
    avatar_url: Mapped[str | None] = mapped_column(Text,nullable=True)
    background_url: Mapped[str | None] = mapped_column(Text,nullable=True)
    bio: Mapped[str | None] = mapped_column(Text,nullable=True)


    # Reletionship (Links from Profile to IgnoreList)

    # List of IgnoreList entries where this profile is the ignorer (the one who ignores others)
    ignored_users_links: Mapped[list["IgnoreList"]] = relationship(
        "IgnoreList", 
        foreign_keys="[IgnoreList.user_id]", 
        back_populates="ignorer",
        cascade="all, delete-orphan"
    )
    
    # List of IgnoreList entries where this profile is the ignored (the one being ignored)
    ignored_by_links: Mapped[list["IgnoreList"]] = relationship(
        "IgnoreList", 
        foreign_keys="[IgnoreList.ignored_user_id]", 
        back_populates="ignored",
        cascade="all, delete-orphan"
    )