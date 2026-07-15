from datetime import datetime
from pydantic import BaseModel, Field

from app.models.coupon import CouponType


class CouponCreate(BaseModel):
   name: str = Field(..., max_length=200, description="优惠券名称")
   type: CouponType
   face_value: float = Field(..., ge=0)
   min_order_amount: float = Field(default=0, ge=0)
   valid_from: datetime
   valid_until: datetime
   applicable_channel: str | None = Field(None, max_length=50)
   applicable_product_id: str | None = None
   notes: str | None = None


class CouponUpdate(BaseModel):
   name: str | None = Field(None, max_length=200)
   type: CouponType | None = None
   face_value: float | None = Field(None, ge=0)
   min_order_amount: float | None = Field(None, ge=0)
   valid_from: datetime | None = None
   valid_until: datetime | None = None
   applicable_channel: str | None = None
   applicable_product_id: str | None = None
   is_used: bool | None = None
   notes: str | None = None


class CouponResponse(BaseModel):
   id: str
   family_id: str
   name: str
   type: CouponType
   face_value: float
   min_order_amount: float
   valid_from: datetime
   valid_until: datetime
   applicable_channel: str | None = None
   applicable_product_id: str | None = None
   is_used: bool
   is_expired_notified: bool
   notes: str | None = None
   created_at: datetime
   model_config = {"from_attributes": True}


class CouponExpiringResponse(CouponResponse):
   days_until_expiry: int = 0
