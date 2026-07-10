from datetime import datetime, timezone

from sqlalchemy import String, Integer, Float, Boolean, Text, DateTime, ForeignKey, Enum as SAEnum
from sqlalchemy.orm import Mapped, mapped_column, relationship
from sqlalchemy.dialects.mysql import CHAR
import enum

from app.database import Base
from app.utils.security import generate_uuid


class Product(Base):
    __tablename__ = "products"

    id: Mapped[str] = mapped_column(CHAR(36), primary_key=True, default=generate_uuid)
    family_id: Mapped[str] = mapped_column(CHAR(36), ForeignKey("families.id"), nullable=False, index=True, comment="所属家庭")
    category_id: Mapped[str] = mapped_column(CHAR(36), ForeignKey("categories.id"), nullable=False, comment="分类")
    name: Mapped[str] = mapped_column(String(200), nullable=False, comment="商品名称")
    brand: Mapped[str | None] = mapped_column(String(100), nullable=True, comment="品牌")
    specification: Mapped[str | None] = mapped_column(String(200), nullable=True, comment="规格")
    unit: Mapped[str] = mapped_column(String(20), default="个", comment="单位")
    current_stock: Mapped[float] = mapped_column(Float, default=0, comment="当前库存")
    monthly_consumption: Mapped[float] = mapped_column(Float, default=0, comment="月均消耗量")
    storage_location: Mapped[str | None] = mapped_column(String(100), nullable=True, comment="存放位置")
    image_url: Mapped[str | None] = mapped_column(String(500), nullable=True, comment="商品图片(OSS)")
    rating: Mapped[int | None] = mapped_column(Integer, nullable=True, comment="评分1-5星")
    repurchase_count: Mapped[int] = mapped_column(Integer, default=0, comment="复购次数")
    is_blacklisted: Mapped[bool] = mapped_column(Boolean, default=False, comment="是否黑名单")
    notes: Mapped[str | None] = mapped_column(Text, nullable=True, comment="备注")
    is_active: Mapped[bool] = mapped_column(Boolean, default=True, comment="是否启用")
    created_at: Mapped[datetime] = mapped_column(DateTime, default=lambda: datetime.now(timezone.utc))
    updated_at: Mapped[datetime] = mapped_column(
        DateTime, default=lambda: datetime.now(timezone.utc), onupdate=lambda: datetime.now(timezone.utc)
    )

    category = relationship("Category")
    purchase_plans = relationship("PurchasePlan", back_populates="product", cascade="all, delete-orphan")

    def __repr__(self) -> str:
        return f"<Product {self.name}>"


class PurchasePlan(Base):
    __tablename__ = "purchase_plans"

    id: Mapped[str] = mapped_column(CHAR(36), primary_key=True, default=generate_uuid)
    product_id: Mapped[str] = mapped_column(CHAR(36), ForeignKey("products.id"), nullable=False, comment="商品")
    is_primary: Mapped[bool] = mapped_column(Boolean, default=False, comment="是否首选方案")
    channel_name: Mapped[str] = mapped_column(String(50), nullable=False, comment="渠道名称")
    product_url: Mapped[str | None] = mapped_column(String(1000), nullable=True, comment="商品链接")
    price: Mapped[float] = mapped_column(Float, default=0, comment="价格")
    shipping_fee: Mapped[float] = mapped_column(Float, default=0, comment="运费")
    notes: Mapped[str | None] = mapped_column(Text, nullable=True, comment="备注")
    created_at: Mapped[datetime] = mapped_column(DateTime, default=lambda: datetime.now(timezone.utc))
    updated_at: Mapped[datetime] = mapped_column(
        DateTime, default=lambda: datetime.now(timezone.utc), onupdate=lambda: datetime.now(timezone.utc)
    )

    product = relationship("Product", back_populates="purchase_plans")
    price_channels = relationship("PriceChannel", back_populates="purchase_plan", cascade="all, delete-orphan")
