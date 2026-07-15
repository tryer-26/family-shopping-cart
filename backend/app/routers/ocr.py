import logging

from fastapi import APIRouter, Depends, HTTPException, UploadFile, File, Form, status
from sqlalchemy.ext.asyncio import AsyncSession

from app.database import get_db
from app.dependencies import get_current_user
from app.models.user import User
from app.schemas.system import OCRResultResponse, OCRLogResponse
from app.crud.family import family_member_crud
from app.crud.system import ocr_log_crud
from app.services.ocr import ocr_service
from app.services.oss import oss_service
from app.tasks.ocr_tasks import process_ocr_recognition

logger = logging.getLogger(__name__)

router = APIRouter(prefix="/ocr", tags=["识图搜品"])


@router.post("/recognize/{family_id}", response_model=OCRResultResponse)
async def recognize_image(
    family_id: str,
    file: UploadFile = File(..., description="商品图片"),
    async_mode: bool = Form(False, description="是否异步处理"),
    current_user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db),
):
    """
    Upload product image for OCR recognition.
    - Sync mode: upload -> OCR -> match -> return result
    - Async mode: upload -> queue Celery task -> return task info
    """
    if not await family_member_crud.is_member(db, family_id, current_user.id):
        raise HTTPException(status_code=403, detail="不是家庭成员")
    
    # Read file
    file_data = await file.read()
    if len(file_data) > 10 * 1024 * 1024:
        raise HTTPException(status_code=400, detail="图片大小不能超过10MB")
    
    # Upload to OSS
    from app.utils.security import generate_uuid
    file_name = f"ocr/{family_id}/{generate_uuid()}_{file.filename}"
    content_type = file.content_type or "image/jpeg"
    image_url = await oss_service.upload_file(file_data, file_name, content_type)
    
    if async_mode:
        # Async: queue Celery task
        task = process_ocr_recognition.delay(image_url, family_id, current_user.id)
        return OCRResultResponse(
            image_url=image_url,
            raw_result={"task_id": task.id, "async": True},
        )
    
    # Sync: process immediately
    result = await ocr_service.recognize(image_url)
    
    # Try to match existing product
    matched_product_id = None
    matched_product_name = None
    matched_product_brand = None
    if result.get("name"):
        from sqlalchemy import select
        from app.models.product import Product
        stmt = select(Product).where(
            Product.family_id == family_id,
            Product.name.ilike(f"%{result['name']}%"),
        )
        product_result = await db.execute(stmt)
        matched = product_result.scalar_one_or_none()
        if matched:
            matched_product_id = matched.id
            matched_product_name = matched.name
            matched_product_brand = matched.brand
    
    # Log
    await ocr_log_crud.create(db, family_id, current_user.id, image_url, result, matched_product_id)
    
    return OCRResultResponse(
        brand=result.get("brand"),
        name=result.get("name"),
        specification=result.get("specification"),
        matched_product_id=matched_product_id,
        matched_product_name=matched_product_name,
        matched_product_brand=matched_product_brand,
        image_url=image_url,
        raw_result=result.get("raw"),
    )


@router.get("/history/{family_id}", response_model=list[OCRLogResponse])
async def get_ocr_history(family_id: str, limit: int = 20,
                           current_user: User = Depends(get_current_user),
                           db: AsyncSession = Depends(get_db)):
    if not await family_member_crud.is_member(db, family_id, current_user.id):
        raise HTTPException(status_code=403, detail="不是家庭成员")
    logs = await ocr_log_crud.get_family_logs(db, family_id, limit)
    return [OCRLogResponse.model_validate(log) for log in logs]


@router.post("/match-product/{log_id}/{product_id}")
async def match_product(log_id: str, product_id: str,
                         current_user: User = Depends(get_current_user),
                         db: AsyncSession = Depends(get_db)):
    """Manually associate an OCR result with a product."""
    from app.crud.system import ocr_log_crud
    log = await ocr_log_crud.update(db, log_id, matched_product_id=product_id)
    if not log:
        raise HTTPException(status_code=404, detail="OCR记录不存在")
    return {"message": "匹配成功"}
