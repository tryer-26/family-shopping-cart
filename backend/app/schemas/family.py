from datetime import datetime
from pydantic import BaseModel, Field

from app.models.family import FamilyRole


class FamilyCreate(BaseModel):
    name: str = Field(..., min_length=1, max_length=100, description="家庭名称")
    description: str | None = Field(None, description="家庭描述")
    emoji: str | None = Field(None, max_length=10, description="图标")


class FamilyUpdate(BaseModel):
    name: str | None = Field(None, min_length=1, max_length=100)
    description: str | None = None
    emoji: str | None = None


class FamilyResponse(BaseModel):
    id: str
    name: str
    description: str | None = None
    emoji: str | None = None
    created_by: str
    created_at: datetime
    model_config = {"from_attributes": True}


class FamilyMemberAdd(BaseModel):
    user_id: str = Field(..., description="用户ID")
    role: FamilyRole = Field(default=FamilyRole.MEMBER, description="角色")


class FamilyMemberUpdate(BaseModel):
    role: FamilyRole = Field(..., description="角色")


class FamilyMemberResponse(BaseModel):
    id: str
    user_id: str
    username: str | None = None
    email: str | None = None
    avatar: str | None = None
    role: FamilyRole
    joined_at: datetime
    model_config = {"from_attributes": True}


class FamilyWithMembers(BaseModel):
    family: FamilyResponse
    members: list[FamilyMemberResponse] = []
    model_config = {"from_attributes": True}
