from fastapi import APIRouter, Depends, HTTPException, Query, status
from sqlalchemy.ext.asyncio import AsyncSession

from app.database import get_db
from app.dependencies import get_current_user
from app.models.user import User
from app.schemas.system import SystemSettingCreate, SystemSettingResponse, SystemSettingUpdate
from app.crud.system import system_setting_crud
from app.crud.family import family_member_crud

router = APIRouter(prefix="/system", tags=["系统设置"])


@router.get("/settings/{family_id}", response_model=list[SystemSettingResponse])
async def get_settings(family_id: str, current_user: User = Depends(get_current_user),
                        db: AsyncSession = Depends(get_db)):
    if not await family_member_crud.is_member(db, family_id, current_user.id):
        raise HTTPException(status_code=403, detail="不是家庭成员")
    settings = await system_setting_crud.get_all(db, family_id)
    return [SystemSettingResponse.model_validate(s) for s in settings]


@router.put("/settings/{family_id}/{key}", response_model=SystemSettingResponse)
async def update_setting(family_id: str, key: str, data: SystemSettingUpdate,
                          current_user: User = Depends(get_current_user),
                          db: AsyncSession = Depends(get_db)):
    if not await family_member_crud.is_admin(db, family_id, current_user.id):
        raise HTTPException(status_code=403, detail="需要管理员权限")
    setting = await system_setting_crud.set(db, family_id, key, data.setting_value or "")
    return SystemSettingResponse.model_validate(setting)


@router.delete("/settings/{family_id}/{key}")
async def delete_setting(family_id: str, key: str,
                          current_user: User = Depends(get_current_user),
                          db: AsyncSession = Depends(get_db)):
    if not await family_member_crud.is_admin(db, family_id, current_user.id):
        raise HTTPException(status_code=403, detail="需要管理员权限")
    success = await system_setting_crud.delete(db, family_id, key)
    if not success:
        raise HTTPException(status_code=404, detail="配置项不存在")
    return {"message": "配置已删除"}


@router.get("/config")
async def get_system_config():
    """Get non-sensitive system configuration for frontend."""
    from app.config import settings
    return {
        "app_name": settings.APP_NAME,
        "app_version": settings.APP_VERSION,
        "meilisearch_available": bool(settings.MEILISEARCH_HOST),
        "oss_configured": bool(settings.OSS_ACCESS_KEY_ID),
        "ocr_configured": bool(settings.OCR_ACCESS_KEY_ID),
        "default_page_size": 20,
        "price_scrape_hours": settings.PRICE_SCRAPE_HOURS,
    }
