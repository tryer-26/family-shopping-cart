from datetime import datetime
from pydantic import BaseModel, EmailStr, Field


class UserCreate(BaseModel):
    username: str = Field(..., min_length=2, max_length=50, description="用户名")
    email: EmailStr = Field(..., description="邮箱")
    password: str = Field(..., min_length=6, max_length=100, description="密码")
    phone: str | None = Field(None, max_length=20, description="手机号")


class UserUpdate(BaseModel):
    username: str | None = Field(None, min_length=2, max_length=50)
    email: EmailStr | None = None
    phone: str | None = Field(None, max_length=20)
    avatar: str | None = None


class UserResponse(BaseModel):
    id: str
    username: str
    email: str
    avatar: str | None = None
    phone: str | None = None
    is_active: bool
    created_at: datetime
    model_config = {"from_attributes": True}


class UserLogin(BaseModel):
    username: str = Field(..., description="用户名或邮箱")
    password: str = Field(..., description="密码")


class TokenResponse(BaseModel):
    access_token: str
    refresh_token: str
    token_type: str = "bearer"
    user: UserResponse


class PasswordChange(BaseModel):
    old_password: str = Field(..., description="旧密码")
    new_password: str = Field(..., min_length=6, description="新密码")
