from datetime import datetime
from pydantic import BaseModel, Field


class CategoryCreate(BaseModel):
    name: str = Field(..., min_length=1, max_length=50, description="分类名称")
    parent_id: str | None = Field(None, description="父分类ID")
    emoji: str | None = Field(None, max_length=10, description="emoji图标")
    sort_order: int = Field(default=0, description="排序")


class CategoryUpdate(BaseModel):
    name: str | None = Field(None, min_length=1, max_length=50)
    parent_id: str | None = None
    emoji: str | None = None
    sort_order: int | None = None
    is_active: bool | None = None


class CategoryResponse(BaseModel):
    id: str
    family_id: str
    name: str
    parent_id: str | None = None
    emoji: str | None = None
    sort_order: int
    is_active: bool
    created_at: datetime
    model_config = {"from_attributes": True}


class CategoryTreeNode(CategoryResponse):
    children: list["CategoryTreeNode"] = []
    model_config = {"from_attributes": True}
