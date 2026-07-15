from datetime import datetime, timezone
from sqlalchemy import select, and_, desc
from sqlalchemy.ext.asyncio import AsyncSession

from app.models.price import PriceChannel, PriceHistory
from app.models.product import Product, PurchasePlan


class PriceChannelCRUD:
   async def create(self, db: AsyncSession, purchase_plan_id: str, **kwargs) -> PriceChannel:
       pc = PriceChannel(purchase_plan_id=purchase_plan_id, **kwargs)
       db.add(pc)
       await db.flush()
       await db.refresh(pc)
       return pc

   async def get_by_plan(self, db: AsyncSession, purchase_plan_id: str) -> list[PriceChannel]:
       result = await db.execute(
           select(PriceChannel).where(PriceChannel.purchase_plan_id == purchase_plan_id)
           .order_by(PriceChannel.final_price.asc())
       )
       return list(result.scalars().all())

   async def update(self, db: AsyncSession, channel_id: str, **kwargs) -> PriceChannel | None:
       result = await db.execute(select(PriceChannel).where(PriceChannel.id == channel_id))
       pc = result.scalar_one_or_none()
       if not pc:
           return None
       for key, value in kwargs.items():
           if value is not None and hasattr(pc, key):
               setattr(pc, key, value)
       await db.flush()
       await db.refresh(pc)
       return pc

   async def delete(self, db: AsyncSession, channel_id: str) -> bool:
       result = await db.execute(select(PriceChannel).where(PriceChannel.id == channel_id))
       pc = result.scalar_one_or_none()
       if not pc:
           return False
       await db.delete(pc)
       await db.flush()
       return True

   async def get_best_price_for_product(self, db: AsyncSession, product_id: str) -> dict | None:
       result = await db.execute(
           select(PriceChannel)
           .join(PurchasePlan, PriceChannel.purchase_plan_id == PurchasePlan.id)
           .where(PurchasePlan.product_id == product_id)
           .order_by(PriceChannel.final_price.asc())
       )
       best = result.scalar_one_or_none()
       if not best:
           return None
       return {
           "product_id": product_id,
           "channel_name": best.channel_name,
           "final_price": best.final_price,
           "product_url": best.product_url,
       }


class PriceHistoryCRUD:
   async def record(self, db: AsyncSession, product_id: str, channel_name: str, price: float,
                    shipping_fee: float = 0, purchase_plan_id: str | None = None) -> PriceHistory:
       ph = PriceHistory(
           product_id=product_id, purchase_plan_id=purchase_plan_id,
           channel_name=channel_name, price=price, shipping_fee=shipping_fee,
       )
       db.add(ph)
       await db.flush()
       return ph

   async def get_history(self, db: AsyncSession, product_id: str,
                         days: int = 90) -> list[PriceHistory]:
       since = datetime.now(timezone.utc).replace(hour=0, minute=0, second=0, microsecond=0)
       from datetime import timedelta
       since = since - timedelta(days=days)
       result = await db.execute(
           select(PriceHistory).where(
               and_(PriceHistory.product_id == product_id, PriceHistory.recorded_at >= since)
           ).order_by(PriceHistory.recorded_at.asc())
       )
       return list(result.scalars().all())


price_channel_crud = PriceChannelCRUD()
price_history_crud = PriceHistoryCRUD()
