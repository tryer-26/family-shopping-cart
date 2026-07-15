import asyncio
import logging

from sqlalchemy import select

from app.tasks.celery_app import celery_app
from app.database import async_session_factory
from app.services.ocr import ocr_service
from app.crud.system import ocr_log_crud
from app.models.product import Product

logger = logging.getLogger(__name__)


@celery_app.task(bind=True, max_retries=2, default_retry_delay=30)
def process_ocr_recognition(self, image_url: str, family_id: str, user_id: str):
    """
    Process OCR recognition asynchronously via Celery.
    Uploads to OSS is done before this task is called.
    """
    logger.info(f"[OCRTask] Processing recognition for image: {image_url}")
    
    async def _run():
        # Call OCR service
        result = await ocr_service.recognize(image_url)
        
        # Try to match with existing products
        matched_product_id = None
        if result.get("name"):
            async with async_session_factory() as db:
                async with db.begin():
                    stmt = select(Product).where(
                        Product.family_id == family_id,
                        Product.name.ilike(f"%{result['name']}%"),
                    )
                    product_result = await db.execute(stmt)
                    matched = product_result.scalar_one_or_none()
                    if matched:
                        matched_product_id = matched.id
                        result["matched_product_id"] = matched.id
                        result["matched_product_name"] = matched.name
                    
                    # Log the recognition
                    await ocr_log_crud.create(
                        db, family_id, user_id, image_url,
                        ocr_result=result,
                        matched_product_id=matched_product_id,
                    )
        
        logger.info(f"[OCRTask] Completed recognition: {result.get('name', 'unknown')}")
        return result
    
    try:
        loop = asyncio.new_event_loop()
        asyncio.set_event_loop(loop)
        return loop.run_until_complete(_run())
    except Exception as e:
        logger.error(f"OCR task failed: {e}")
        raise self.retry(exc=e)
