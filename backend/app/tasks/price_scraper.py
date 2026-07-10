 """
 Price scraping tasks using Celery.
 
 DISCLAIMER: This module is for personal/family use only.
 Commercial use and high-frequency crawling are strictly prohibited.
 """
 
 import asyncio
 import logging
 
 from app.tasks.celery_app import celery_app
 from app.services.scraper import registry, detect_platform
 from app.services.scraper_example import registry as example_registry
 from app.database import async_session_factory
 from app.crud.price import price_channel_crud, price_history_crud
 from app.models.price import PriceChannel
 
 logger = logging.getLogger(__name__)
 
 
 @celery_app.task(bind=True, max_retries=3, default_retry_delay=60)
 def scrape_product_price(self, product_id: str, url: str, price_channel_id: str | None = None):
     """
     Scrape a single product's price from a given URL.
     
     DISCLAIMER: For personal/family use only.
     """
     logger.info(f"[ScrapeTask] Starting price scrape for product {product_id}, URL: {url}")
     
     async def _run():
         platform = detect_platform(url)
         if not platform:
             logger.warning(f"Unknown platform for URL: {url}")
             return {"error": "unknown_platform", "product_id": product_id}
         
         scraper = registry.get(platform)
         if not scraper:
             logger.warning(f"No scraper registered for platform: {platform}")
             return {"error": "no_scraper", "product_id": product_id}
         
         result = await scraper.scrape(url)
         if not result.success:
             logger.error(f"Scrape failed for {url}: {result.error}")
             return {"error": result.error, "product_id": product_id}
         
         # Save to database
         async with async_session_factory() as db:
             async with db.begin():
                 if price_channel_id:
                     await price_channel_crud.update(
                         db, price_channel_id,
                         final_price=result.final_price,
                         list_price=result.list_price,
                         shipping_fee=result.shipping_fee,
                     )
                 await price_history_crud.record(
                     db, product_id, result.channel_name,
                     result.final_price, result.shipping_fee,
                 )
         
         logger.info(f"[ScrapeTask] Completed: {result.title} @ {result.final_price}")
         return {
             "success": True,
             "product_id": product_id,
             "price": result.final_price,
             "channel": result.channel_name,
         }
     
     try:
         loop = asyncio.new_event_loop()
         asyncio.set_event_loop(loop)
         return loop.run_until_complete(_run())
     except Exception as e:
         logger.error(f"Scrape task failed for {product_id}: {e}")
         raise self.retry(exc=e)
 
 
 @celery_app.task(bind=True)
 def batch_scrape_prices(self, product_urls: list[dict]):
     """
     Batch scrape prices for multiple products.
     
     DISCLAIMER: For personal/family use only.
     Each product_url item: {"product_id": str, "url": str, "price_channel_id": str | None}
     """
     results = []
     for item in product_urls:
         try:
             result = scrape_product_price.delay(
                 item["product_id"], item["url"], item.get("price_channel_id")
             )
             results.append(result.id)
         except Exception as e:
             logger.error(f"Failed to queue scrape for {item.get('product_id')}: {e}")
     return {"queued": len(results), "task_ids": results}
