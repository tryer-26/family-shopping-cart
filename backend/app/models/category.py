import uuid
from datetime import datetime, timezone

from sqlalchemy import String, Integer, Boolean, DateTime, ForeignKey, UniqueConstraint
from sqlalchemy.orm import Mapped, mapped_column, relationship
from sqlalchemy.dialects.mysql import CHAR

from app.database import Base
from app.utils.security import generate_uuid


class Category(Base):
    __tablename__ = "categories"

    id: Mapped[str] = mapped_column(CHAR(36), primary_key=True, default=generate_uuid)
    family_id: Mapped[str] = mapped_column(CHAR(36), ForeignKey("families.id"), nullable=False, comment="所属家庭")
    name: Mapped[str] = mapped_column(String(50), nullable=False, comment="分类名称")
    parent_id: Mapped[str | None] = mapped_column(CHAR(36), ForeignKey("categories.id"), nullable=True, comment="父分类ID")
    emoji: Mapped[str | None] = mapped_column(String(10), nullable=True, comment="emoji图标")
    sort_order: Mapped[int] = mapped_column(Integer, default=0, comment="排序")
    is_active: Mapped[bool] = mapped_column(Boolean, default=True, comment="是否启用")
    created_at: Mapped[datetime] = mapped_column(DateTime, default=lambda: datetime.now(timezone.utc))
    updated_at: Mapped[datetime] = mapped_column(
        DateTime, default=lambda: datetime.now(timezone.utc), onupdate=lambda: datetime.now(timezone.utc)
    )

    parent = relationship("Category", remote_side="Category.id", backref="children")

    __table_args__ = (
        UniqueConstraint("family_id", "name", name="uq_category_family_name"),
    )

    def __repr__(self) -> str:
        return f"<Category {self.name}>"
