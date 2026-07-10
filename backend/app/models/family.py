import uuid
from datetime import datetime, timezone

from sqlalchemy import String, Text, DateTime, ForeignKey, Enum as SAEnum, UniqueConstraint
from sqlalchemy.orm import Mapped, mapped_column, relationship
from sqlalchemy.dialects.mysql import CHAR
import enum

from app.database import Base
from app.utils.security import generate_uuid


class FamilyRole(str, enum.Enum):
    ADMIN = "admin"
    MEMBER = "member"


class Family(Base):
    __tablename__ = "families"

    id: Mapped[str] = mapped_column(CHAR(36), primary_key=True, default=generate_uuid)
    name: Mapped[str] = mapped_column(String(100), nullable=False, comment="家庭名称")
    description: Mapped[str | None] = mapped_column(Text, nullable=True, comment="家庭描述")
    emoji: Mapped[str | None] = mapped_column(String(10), nullable=True, comment="家庭图标emoji")
    created_by: Mapped[str] = mapped_column(CHAR(36), ForeignKey("users.id"), nullable=False, comment="创建者")
    created_at: Mapped[datetime] = mapped_column(DateTime, default=lambda: datetime.now(timezone.utc))
    updated_at: Mapped[datetime] = mapped_column(
        DateTime, default=lambda: datetime.now(timezone.utc), onupdate=lambda: datetime.now(timezone.utc)
    )

    creator = relationship("User", foreign_keys=[created_by])
    members = relationship("FamilyMember", back_populates="family", cascade="all, delete-orphan")

    def __repr__(self) -> str:
        return f"<Family {self.name}>"


class FamilyMember(Base):
    __tablename__ = "family_members"

    id: Mapped[str] = mapped_column(CHAR(36), primary_key=True, default=generate_uuid)
    family_id: Mapped[str] = mapped_column(CHAR(36), ForeignKey("families.id"), nullable=False)
    user_id: Mapped[str] = mapped_column(CHAR(36), ForeignKey("users.id"), nullable=False)
    role: Mapped[FamilyRole] = mapped_column(SAEnum(FamilyRole), default=FamilyRole.MEMBER, comment="角色")
    joined_at: Mapped[datetime] = mapped_column(DateTime, default=lambda: datetime.now(timezone.utc))

    __table_args__ = (
        UniqueConstraint("family_id", "user_id", name="uq_family_user"),
    )

    family = relationship("Family", back_populates="members")
    user = relationship("User")
