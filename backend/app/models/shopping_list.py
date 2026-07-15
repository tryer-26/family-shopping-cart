from datetime import datetime, timezone

from sqlalchemy import String, Float, Integer, Text, DateTime, ForeignKey, Enum as SAEnum
from sqlalchemy.orm import Mapped, mapped_column, relationship
from sqlalchemy.dialects.mysql import CHAR
import enum

from app.database import Base
from app.utils.security import generate_uuid


class ShoppingItemStatus(str, enum.Enum):
    PENDING = "pending"
    PURCHASED = "purchased"
    CANCELLED = "cancelled"


class ShoppingListItem(Base):
    __tablename__ = "shopping_list_items"

    id: Mapped[str] = mapped_column(CHAR(36), primary_key=True, default=generate_uuid)
    family_id: Mapped[str] = mapped_column(CHAR(36), ForeignKey("families.id"), nullable=False, index=True, comment="所属家庭")
    product_id: Mapped[str] = mapped_column(CHAR(36), ForeignKey("products.id"), nullable=False, comment="商品")
    purchase_plan_id: Mapped[str | None] = mapped_column(CHAR(36), ForeignKey("purchase_plans.id"), nullable=True, comment="选定采购方案")
    quantity: Mapped[float] = mapped_column(Float, default=1, comment="数量")
    estimated_price: Mapped[float | None] = mapped_column(Float, nullable=True, comment="预估价格")
    actual_price: Mapped[float | None] = mapped_column(Float, nullable=True, comment="实际价格")
    status: Mapped[ShoppingItemStatus] = mapped_column(
        SAEnum(ShoppingItemStatus), default=ShoppingItemStatus.PENDING, comment="状态"
    )
    added_by: Mapped[str] = mapped_column(CHAR(36), ForeignKey("users.id"), nullable=False, comment="添加人")
    purchased_by: Mapped[str | None] = mapped_column(CHAR(36), ForeignKey("users.id"), nullable=True, comment="购买人")
    notes: Mapped[str | None] = mapped_column(Text, nullable=True, comment="备注")
    created_at: Mapped[datetime] = mapped_column(DateTime, default=lambda: datetime.now(timezone.utc))
    updated_at: Mapped[datetime] = mapped_column(
        DateTime, default=lambda: datetime.now(timezone.utc), onupdate=lambda: datetime.now(timezone.utc)
    )

    product = relationship("Product")
    purchase_plan = relationship("PurchasePlan")
