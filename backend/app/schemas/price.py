from datetime import datetime
from pydantic import BaseModel, Field


class PriceChannelCreate(BaseModel):
    channel_name: str = Field(..., max_length=50, description="渠道名")
    product_url: str | None = Field(None, description="商品链接")
    list_price: float = Field(default=0, ge=0)
    final_price: float = Field(default=0, ge=0, description="到手价")
    shipping_fee: float = Field(default=0, ge=0)


class PriceChannelUpdate(BaseModel):
    channel_name: str | None = Field(None, max_length=50)
    product_url: str | None = None
    list_price: float | None = Field(None, ge=0)
    final_price: float | None = Field(None, ge=0)
    shipping_fee: float | None = Field(None, ge=0)


class PriceChannelResponse(BaseModel):
    id: str
    purchase_plan_id: str
    channel_name: str
    product_url: str | None = None
    list_price: float
    final_price: float
    shipping_fee: float
    updated_at: datetime
    model_config = {"from_attributes": True}


class PriceHistoryResponse(BaseModel):
    id: str
    product_id: str
    channel_name: str
    price: float
    shipping_fee: float
    recorded_at: datetime
    model_config = {"from_attributes": True}


class BestPriceResponse(BaseModel):
    product_id: str
    product_name: str
    channel_name: str
    final_price: float
    product_url: str | None = None
    coupon_discount: float = 0
    model_config = {"from_attributes": True}
