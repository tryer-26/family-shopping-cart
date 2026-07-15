from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.ext.asyncio import AsyncSession

from app.database import get_db
from app.dependencies import get_current_user
from app.schemas.user import UserCreate, UserLogin, TokenResponse, UserResponse, PasswordChange
from app.crud.user import user_crud
from app.utils.security import create_access_token, create_refresh_token, decode_access_token
from app.models.user import User

router = APIRouter(prefix="/auth", tags=["认证"])


@router.post("/register", response_model=TokenResponse, status_code=status.HTTP_201_CREATED)
async def register(data: UserCreate, db: AsyncSession = Depends(get_db)):
    """Register a new user."""
    existing = await user_crud.get_by_username(db, data.username)
    if existing:
        raise HTTPException(status_code=400, detail="用户名已存在")
    existing_email = await user_crud.get_by_email(db, data.email)
    if existing_email:
        raise HTTPException(status_code=400, detail="邮箱已被注册")
    user = await user_crud.create(db, data.username, data.email, data.password, data.phone)
    access_token = create_access_token(user.id)
    refresh_token = create_refresh_token(user.id)
    return TokenResponse(
        access_token=access_token, refresh_token=refresh_token,
        user=UserResponse.model_validate(user),
    )


@router.post("/login", response_model=TokenResponse)
async def login(data: UserLogin, db: AsyncSession = Depends(get_db)):
    """Login with username/email and password."""
    user = await user_crud.authenticate(db, data.username, data.password)
    if not user:
        raise HTTPException(status_code=401, detail="用户名或密码错误")
    access_token = create_access_token(user.id)
    refresh_token = create_refresh_token(user.id)
    return TokenResponse(
        access_token=access_token, refresh_token=refresh_token,
        user=UserResponse.model_validate(user),
    )


@router.post("/refresh", response_model=TokenResponse)
async def refresh_token(refresh_token: str, db: AsyncSession = Depends(get_db)):
    """Refresh access token using refresh token."""
    payload = decode_access_token(refresh_token)
    if payload is None or payload.get("type") != "refresh":
        raise HTTPException(status_code=401, detail="无效的刷新令牌")
    user_id = payload.get("sub")
    user = await user_crud.get_by_id(db, user_id)
    if not user or not user.is_active:
        raise HTTPException(status_code=401, detail="用户不存在或已禁用")
    new_access = create_access_token(user.id)
    new_refresh = create_refresh_token(user.id)
    return TokenResponse(
        access_token=new_access, refresh_token=new_refresh,
        user=UserResponse.model_validate(user),
    )


@router.get("/me", response_model=UserResponse)
async def get_me(current_user: User = Depends(get_current_user)):
    """Get current user info."""
    return UserResponse.model_validate(current_user)


@router.put("/password")
async def change_password(data: PasswordChange, current_user: User = Depends(get_current_user),
                          db: AsyncSession = Depends(get_db)):
    """Change password."""
    success = await user_crud.change_password(db, current_user.id, data.old_password, data.new_password)
    if not success:
        raise HTTPException(status_code=400, detail="原密码错误")
    return {"message": "密码修改成功"}


@router.put("/me", response_model=UserResponse)
async def update_profile(data: dict, current_user: User = Depends(get_current_user),
                         db: AsyncSession = Depends(get_db)):
    """Update user profile."""
    allowed_fields = {"username", "email", "phone", "avatar"}
    update_data = {k: v for k, v in data.items() if k in allowed_fields and v is not None}
    if not update_data:
        raise HTTPException(status_code=400, detail="没有需要更新的字段")
    user = await user_crud.update(db, current_user.id, **update_data)
    return UserResponse.model_validate(user)
