from datetime import datetime, timezone

from sqlalchemy import String, Float, DateTime, ForeignKey, Text
from sqlalchemy.orm import Mapped, mapped_column, relationship
from sqlalchemy.dialects.mysql import CHAR

from app.database import Base
from app.utils.security import generate_uuid


class PriceChannel(Base):
    __tablename__ = "price_channels"

    id: Mapped[str] = mapped_column(CHAR(36), primary_key=True, default=generate_uuid)
    purchase_plan_id: Mapped[str] = mapped_column(CHAR(36), ForeignKey("purchase_plans.id"), nullable=False, comment="采购方案")
    channel_name: Mapped[str] = mapped_column(String(50), nullable=False, comment="渠道名(京东/淘宝/拼多多等)")
    product_url: Mapped[str | None] = mapped_column(String(1000), nullable=True, comment="商品链接")
    list_price: Mapped[float] = mapped_column(Float, default=0, comment="标价")
    final_price: Mapped[float] = mapped_column(Float, default=0, comment="到手价(叠加优惠后)")
    shipping_fee: Mapped[float] = mapped_column(Float, default=0, comment="运费")
    updated_at: Mapped[datetime] = mapped_column(
        DateTime, default=lambda: datetime.now(timezone.utc), onupdate=lambda: datetime.now(timezone.utc), comment="更新时间"
    )

    purchase_plan = relationship("PurchasePlan", back_populates="price_channels")


class PriceHistory(Base):
    __tablename__ = "price_histories"

    id: Mapped[str] = mapped_column(CHAR(36), primary_key=True, default=generate_uuid)
    product_id: Mapped[str] = mapped_column(CHAR(36), ForeignKey("products.id"), nullable=False, index=True, comment="商品")
    purchase_plan_id: Mapped[str | None] = mapped_column(CHAR(36), ForeignKey("purchase_plans.id"), nullable=True, comment="采购方案")
    channel_name: Mapped[str] = mapped_column(String(50), nullable=False, comment="渠道")
    price: Mapped[float] = mapped_column(Float, default=0, comment="价格")
    shipping_fee: Mapped[float] = mapped_column(Float, default=0, comment="运费")
    recorded_at: Mapped[datetime] = mapped_column(DateTime, default=lambda: datetime.now(timezone.utc), comment="记录时间")
