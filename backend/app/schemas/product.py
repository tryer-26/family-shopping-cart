from datetime import datetime
from pydantic import BaseModel, Field


class PurchasePlanCreate(BaseModel):
   is_primary: bool = False
   channel_name: str = Field(..., max_length=50, description="渠道名称")
   product_url: str | None = Field(None, description="商品链接")
   price: float = Field(default=0, ge=0)
   shipping_fee: float = Field(default=0, ge=0)
   notes: str | None = None


class PurchasePlanUpdate(BaseModel):
   is_primary: bool | None = None
   channel_name: str | None = Field(None, max_length=50)
   product_url: str | None = None
   price: float | None = Field(None, ge=0)
   shipping_fee: float | None = Field(None, ge=0)
   notes: str | None = None


class PurchasePlanResponse(BaseModel):
   id: str
   product_id: str
   is_primary: bool
   channel_name: str
   product_url: str | None = None
   price: float
   shipping_fee: float
   notes: str | None = None
   created_at: datetime
   model_config = {"from_attributes": True}


class ProductCreate(BaseModel):
   category_id: str = Field(..., description="分类ID")
   name: str = Field(..., min_length=1, max_length=200, description="商品名称")
   brand: str | None = Field(None, max_length=100)
   specification: str | None = Field(None, max_length=200)
   unit: str = Field(default="个", max_length=20)
   current_stock: float = Field(default=0, ge=0)
   monthly_consumption: float = Field(default=0, ge=0)
   storage_location: str | None = Field(None, max_length=100)
   image_url: str | None = None
   notes: str | None = None
   purchase_plans: list[PurchasePlanCreate] = []


class ProductUpdate(BaseModel):
   category_id: str | None = None
   name: str | None = Field(None, min_length=1, max_length=200)
   brand: str | None = None
   specification: str | None = None
   unit: str | None = Field(None, max_length=20)
   current_stock: float | None = Field(None, ge=0)
   monthly_consumption: float | None = Field(None, ge=0)
   storage_location: str | None = None
   image_url: str | None = None
   rating: int | None = Field(None, ge=1, le=5)
   is_blacklisted: bool | None = None
   notes: str | None = None
   is_active: bool | None = None


class ProductResponse(BaseModel):
   id: str
   family_id: str
   category_id: str
   name: str
   brand: str | None = None
   specification: str | None = None
   unit: str
   current_stock: float
   monthly_consumption: float
   storage_location: str | None = None
   image_url: str | None = None
   rating: int | None = None
   repurchase_count: int
   is_blacklisted: bool
   notes: str | None = None
   is_active: bool
   created_at: datetime
   model_config = {"from_attributes": True}


class ProductDetail(ProductResponse):
   category_name: str | None = None
   purchase_plans: list[PurchasePlanResponse] = []
   days_until_out_of_stock: float | None = None
   best_channel: str | None = None
   best_price: float | None = None
   model_config = {"from_attributes": True}
