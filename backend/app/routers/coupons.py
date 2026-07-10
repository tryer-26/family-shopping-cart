 from fastapi import APIRouter, Depends, HTTPException, Query, status
 from sqlalchemy.ext.asyncio import AsyncSession
 from datetime import datetime, timezone
 
 from app.database import get_db
 from app.dependencies import get_current_user
 from app.models.user import User
 from app.schemas.coupon import CouponCreate, CouponUpdate, CouponResponse, CouponExpiringResponse
 from app.crud.coupon import coupon_crud
 from app.crud.family import family_member_crud
 from app.utils.pagination import PaginationParams, PaginatedResult
 
 router = APIRouter(prefix="/coupons", tags=["优惠券管理"])
 
 
 @router.post("/family/{family_id}", response_model=CouponResponse, status_code=201)
 async def create_coupon(family_id: str, data: CouponCreate,
                          current_user: User = Depends(get_current_user),
                          db: AsyncSession = Depends(get_db)):
     if not await family_member_crud.is_member(db, family_id, current_user.id):
         raise HTTPException(status_code=403, detail="不是家庭成员")
     coupon = await coupon_crud.create(db, family_id, **data.model_dump())
     return CouponResponse.model_validate(coupon)
 
 
 @router.get("/family/{family_id}", response_model=PaginatedResult)
 async def list_coupons(family_id: str, page: int = Query(1, ge=1),
                         page_size: int = Query(20, ge=1, le=100),
                         current_user: User = Depends(get_current_user),
                         db: AsyncSession = Depends(get_db)):
     if not await family_member_crud.is_member(db, family_id, current_user.id):
         raise HTTPException(status_code=403, detail="不是家庭成员")
     params = PaginationParams(page, page_size)
     result = await coupon_crud.get_family_coupons(db, family_id, params)
     result.items = [CouponResponse.model_validate(c) for c in result.items]
     return result
 
 
 @router.get("/family/{family_id}/expiring", response_model=list[CouponExpiringResponse])
 async def get_expiring_coupons(family_id: str, within_days: int = Query(7, ge=1, le=30),
                                 current_user: User = Depends(get_current_user),
                                 db: AsyncSession = Depends(get_db)):
     if not await family_member_crud.is_member(db, family_id, current_user.id):
         raise HTTPException(status_code=403, detail="不是家庭成员")
     coupons = await coupon_crud.get_expiring_coupons(db, family_id, within_days)
     result = []
     for c in coupons:
         r = CouponExpiringResponse.model_validate(c)
         r.days_until_expiry = (c.valid_until - datetime.now(timezone.utc)).days
         result.append(r)
     return result
 
 
 @router.put("/{coupon_id}", response_model=CouponResponse)
 async def update_coupon(coupon_id: str, data: CouponUpdate,
                          current_user: User = Depends(get_current_user),
                          db: AsyncSession = Depends(get_db)):
     coupon = await coupon_crud.update(db, coupon_id, **data.model_dump(exclude_none=True))
     if not coupon:
         raise HTTPException(status_code=404, detail="优惠券不存在")
     return CouponResponse.model_validate(coupon)
 
 
 @router.delete("/{coupon_id}")
 async def delete_coupon(coupon_id: str, current_user: User = Depends(get_current_user),
                          db: AsyncSession = Depends(get_db)):
     success = await coupon_crud.delete(db, coupon_id)
     if not success:
         raise HTTPException(status_code=404, detail="优惠券不存在")
     return {"message": "优惠券已删除"}
 
 
 @router.post("/{coupon_id}/use")
 async def mark_coupon_used(coupon_id: str, current_user: User = Depends(get_current_user),
                             db: AsyncSession = Depends(get_db)):
     coupon = await coupon_crud.update(db, coupon_id, is_used=True)
     if not coupon:
         raise HTTPException(status_code=404, detail="优惠券不存在")
     return {"message": "优惠券已标记为已使用"}
