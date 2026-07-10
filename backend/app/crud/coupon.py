from datetime import datetime, timezone
from sqlalchemy import select, and_
from sqlalchemy.ext.asyncio import AsyncSession

from app.models.coupon import Coupon
from app.utils.pagination import paginate, PaginationParams, PaginatedResult


class CouponCRUD:
    async def create(self, db: AsyncSession, family_id: str, **kwargs) -> Coupon:
        coupon = Coupon(family_id=family_id, **kwargs)
        db.add(coupon)
        await db.flush()
        await db.refresh(coupon)
        return coupon

    async def get_by_id(self, db: AsyncSession, coupon_id: str) -> Coupon | None:
        result = await db.execute(select(Coupon).where(Coupon.id == coupon_id))
        return result.scalar_one_or_none()

    async def get_family_coupons(self, db: AsyncSession, family_id: str,
                                 params: PaginationParams | None = None) -> PaginatedResult:
        stmt = select(Coupon).where(Coupon.family_id == family_id).order_by(Coupon.valid_until.asc())
        if params:
            return await paginate(db, stmt, params)
        result = await db.execute(stmt)
        items = list(result.scalars().all())
        return PaginatedResult(items=items, total=len(items), page=1, page_size=len(items), total_pages=1)

    async def get_expiring_coupons(self, db: AsyncSession, family_id: str,
                                   within_days: int = 7) -> list[Coupon]:
        now = datetime.now(timezone.utc)
        from datetime import timedelta
        deadline = now + timedelta(days=within_days)
        result = await db.execute(
            select(Coupon).where(
                and_(
                    Coupon.family_id == family_id,
                    Coupon.is_used == False,
                    Coupon.valid_until >= now,
                    Coupon.valid_until <= deadline,
                    Coupon.is_expired_notified == False,
                )
            )
        )
        return list(result.scalars().all())

    async def update(self, db: AsyncSession, coupon_id: str, **kwargs) -> Coupon | None:
        coupon = await self.get_by_id(db, coupon_id)
        if not coupon:
            return None
        for key, value in kwargs.items():
            if value is not None and hasattr(coupon, key):
                setattr(coupon, key, value)
        await db.flush()
        await db.refresh(coupon)
        return coupon

    async def delete(self, db: AsyncSession, coupon_id: str) -> bool:
        coupon = await self.get_by_id(db, coupon_id)
        if not coupon:
            return False
        await db.delete(coupon)
        await db.flush()
        return True


coupon_crud = CouponCRUD()
