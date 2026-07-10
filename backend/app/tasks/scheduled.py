 """
 Scheduled tasks for Celery Beat.
 
 DISCLAIMER: This module is for personal/family use only.
 """
 
 import asyncio
 import logging
 from datetime import datetime, timezone
 
 from sqlalchemy import select
 
 from app.tasks.celery_app import celery_app
 from app.database import async_session_factory
 from app.models.family import Family
 from app.crud.product import product_crud
 from app.crud.coupon import coupon_crud
 from app.crud.system import system_setting_crud
 
 logger = logging.getLogger(__name__)
 
 
 @celery_app.task
 def scheduled_price_scrape():
     """
     Scheduled price scraping task.
     DISCLAIMER: For personal/family use only.
     """
     logger.info("[Scheduled] Running scheduled price scrape")
     # In production, this would iterate over all products with URLs
     # and queue scrape tasks. For now, it logs and returns.
     logger.info("[Scheduled] Price scrape cycle completed")
     return {"status": "completed", "task": "scheduled_price_scrape"}
 
 
 @celery_app.task
 def check_low_stock():
     """
     Check all families for low stock products and log alerts.
     """
     logger.info("[Scheduled] Checking low stock products")
     
     async def _run():
         async with async_session_factory() as db:
             async with db.begin():
                 families_result = await db.execute(select(Family.id))
                 family_ids = [row[0] for row in families_result.all()]
                 
                 for family_id in family_ids:
                     low_stock = await product_crud.get_low_stock_products(db, family_id)
                     if low_stock:
                         names = [p.name for p in low_stock]
                         logger.info(f"Family {family_id}: {len(low_stock)} low stock items: {names}")
                     else:
                         logger.info(f"Family {family_id}: no low stock items")
         
         return {"scanned_families": len(family_ids)}
     
     loop = asyncio.new_event_loop()
     asyncio.set_event_loop(loop)
     return loop.run_until_complete(_run())
 
 
 @celery_app.task
 def check_expiring_coupons():
     """
     Check for coupons expiring within 7 days and log alerts.
     """
     logger.info("[Scheduled] Checking expiring coupons")
     
     async def _run():
         async with async_session_factory() as db:
             async with db.begin():
                 families_result = await db.execute(select(Family.id))
                 family_ids = [row[0] for row in families_result.all()]
                 
                 for family_id in family_ids:
                     expiring = await coupon_crud.get_expiring_coupons(db, family_id)
                     for coupon in expiring:
                         coupon.is_expired_notified = True
                         logger.info(
                             f"Family {family_id}: Coupon '{coupon.name}' expires "
                             f"at {coupon.valid_until}"
                         )
         
         return {"checked_families": len(family_ids)}
     
     loop = asyncio.new_event_loop()
     asyncio.set_event_loop(loop)
     return loop.run_until_complete(_run())
