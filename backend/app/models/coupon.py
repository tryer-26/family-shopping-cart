from datetime import datetime, timezone

from sqlalchemy import String, Float, Boolean, Text, DateTime, ForeignKey, Enum as SAEnum
from sqlalchemy.orm import Mapped, mapped_column, relationship
from sqlalchemy.dialects.mysql import CHAR
import enum

from app.database import Base
from app.utils.security import generate_uuid


class CouponType(str, enum.Enum):
    FILL_REDUCTION = "满减"
    DISCOUNT = "折扣"
    DIRECT_DOWN = "直降"


class Coupon(Base):
    __tablename__ = "coupons"

    id: Mapped[str] = mapped_column(CHAR(36), primary_key=True, default=generate_uuid)
    family_id: Mapped[str] = mapped_column(CHAR(36), ForeignKey("families.id"), nullable=False, index=True, comment="所属家庭")
    name: Mapped[str] = mapped_column(String(200), nullable=False, comment="优惠券名称")
    type: Mapped[CouponType] = mapped_column(SAEnum(CouponType), nullable=False, comment="类型")
    face_value: Mapped[float] = mapped_column(Float, default=0, comment="面额")
    min_order_amount: Mapped[float] = mapped_column(Float, default=0, comment="门槛金额")
    valid_from: Mapped[datetime] = mapped_column(DateTime, nullable=False, comment="有效期开始")
    valid_until: Mapped[datetime] = mapped_column(DateTime, nullable=False, comment="有效期结束")
    applicable_channel: Mapped[str | None] = mapped_column(String(50), nullable=True, comment="适用渠道")
    applicable_product_id: Mapped[str | None] = mapped_column(CHAR(36), ForeignKey("products.id"), nullable=True, comment="适用商品")
    is_used: Mapped[bool] = mapped_column(Boolean, default=False, comment="是否已用")
    is_expired_notified: Mapped[bool] = mapped_column(Boolean, default=False, comment="是否已发送过期提醒")
    notes: Mapped[str | None] = mapped_column(Text, nullable=True, comment="备注")
    created_at: Mapped[datetime] = mapped_column(DateTime, default=lambda: datetime.now(timezone.utc))
