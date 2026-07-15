from fastapi import APIRouter, Depends, HTTPException, Query
from sqlalchemy.ext.asyncio import AsyncSession

from app.database import get_db
from app.dependencies import get_current_user
from app.models.user import User
from app.crud.family import family_member_crud
from app.services.statistics import (
    get_dashboard_stats,
    get_monthly_report,
    get_yearly_comparison,
)

router = APIRouter(prefix="/statistics", tags=["数据统计"])


@router.get("/dashboard/{family_id}")
async def dashboard(family_id: str, current_user: User = Depends(get_current_user),
                     db: AsyncSession = Depends(get_db)):
    if not await family_member_crud.is_member(db, family_id, current_user.id):
        raise HTTPException(status_code=403, detail="不是家庭成员")
    return await get_dashboard_stats(db, family_id)


@router.get("/monthly/{family_id}")
async def monthly_report(family_id: str, year: int = Query(2026, ge=2020),
                          month: int = Query(1, ge=1, le=12),
                          current_user: User = Depends(get_current_user),
                          db: AsyncSession = Depends(get_db)):
    if not await family_member_crud.is_member(db, family_id, current_user.id):
        raise HTTPException(status_code=403, detail="不是家庭成员")
    return await get_monthly_report(db, family_id, year, month)


@router.get("/yearly/{family_id}")
async def yearly_comparison(family_id: str, year: int = Query(2026, ge=2020),
                             current_user: User = Depends(get_current_user),
                             db: AsyncSession = Depends(get_db)):
    if not await family_member_crud.is_member(db, family_id, current_user.id):
        raise HTTPException(status_code=403, detail="不是家庭成员")
    return await get_yearly_comparison(db, family_id, year)
