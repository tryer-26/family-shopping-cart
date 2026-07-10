from datetime import datetime
from pydantic import BaseModel, Field

from app.models.shopping_list import ShoppingItemStatus


class ShoppingListItemCreate(BaseModel):
    product_id: str = Field(..., description="商品ID")
    purchase_plan_id: str | None = None
    quantity: float = Field(default=1, ge=0.01)
    notes: str | None = None


class ShoppingListItemUpdate(BaseModel):
    quantity: float | None = Field(None, ge=0.01)
    status: ShoppingItemStatus | None = None
    purchase_plan_id: str | None = None
    actual_price: float | None = Field(None, ge=0)
    notes: str | None = None


class ShoppingListItemResponse(BaseModel):
    id: str
    family_id: str
    product_id: str
    product_name: str | None = None
    product_unit: str | None = None
    category_name: str | None = None
    purchase_plan_id: str | None = None
    plan_channel_name: str | None = None
    plan_price: float | None = None
    quantity: float
    estimated_price: float | None = None
    actual_price: float | None = None
    status: ShoppingItemStatus
    added_by: str
    added_by_name: str | None = None
    purchased_by: str | None = None
    notes: str | None = None
    created_at: datetime
    model_config = {"from_attributes": True}


class ShoppingListBatchAdd(BaseModel):
    items: list[ShoppingListItemCreate] = Field(..., min_length=1, max_length=50, description="待添加商品列表")


class ShoppingListStats(BaseModel):
    total_items: int = 0
    pending_count: int = 0
    purchased_count: int = 0
    estimated_total: float = 0
    actual_total: float = 0
