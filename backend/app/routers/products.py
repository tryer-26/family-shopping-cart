from fastapi import APIRouter, Depends, HTTPException, status, Query
from sqlalchemy.ext.asyncio import AsyncSession

from app.database import get_db
from app.dependencies import get_current_user
from app.models.user import User
from app.schemas.product import (
    ProductCreate, ProductUpdate, ProductResponse, ProductDetail,
    PurchasePlanCreate, PurchasePlanUpdate, PurchasePlanResponse,
)
from app.crud.product import product_crud, purchase_plan_crud
from app.crud.family import family_member_crud
from app.utils.pagination import PaginationParams, PaginatedResult
from app.services.meilisearch import sync_product as sync_to_meili, remove_product as remove_from_meili

router = APIRouter(prefix="/products", tags=["商品管理"])


@router.post("/family/{family_id}", response_model=ProductResponse, status_code=201)
async def create_product(family_id: str, data: ProductCreate,
                          current_user: User = Depends(get_current_user),
                          db: AsyncSession = Depends(get_db)):
    if not await family_member_crud.is_member(db, family_id, current_user.id):
        raise HTTPException(status_code=403, detail="不是家庭成员")
    product = await product_crud.create(
        db, family_id, data.category_id, data.name,
        brand=data.brand, specification=data.specification, unit=data.unit,
        current_stock=data.current_stock, monthly_consumption=data.monthly_consumption,
        storage_location=data.storage_location, image_url=data.image_url, notes=data.notes,
    )
    # Create purchase plans
    for plan_data in data.purchase_plans:
        await purchase_plan_crud.create(
            db, product.id, **plan_data.model_dump()
        )
    await db.refresh(product)
    try:
        await sync_to_meili(product, data.category_id)
    except Exception as e:
        pass  # Meilisearch sync is best-effort
    return ProductResponse.model_validate(product)


@router.get("/family/{family_id}", response_model=PaginatedResult)
async def list_products(family_id: str, category_id: str | None = Query(None),
                         keyword: str | None = Query(None), page: int = Query(1, ge=1),
                         page_size: int = Query(20, ge=1, le=100),
                         current_user: User = Depends(get_current_user),
                         db: AsyncSession = Depends(get_db)):
    if not await family_member_crud.is_member(db, family_id, current_user.id):
        raise HTTPException(status_code=403, detail="不是家庭成员")
    params = PaginationParams(page, page_size)
    result = await product_crud.get_family_products(
        db, family_id, category_id=category_id, keyword=keyword, params=params
    )
    # Convert to response models
    result.items = [ProductResponse.model_validate(p) for p in result.items]
    return result


@router.get("/{product_id}", response_model=ProductDetail)
async def get_product(product_id: str, current_user: User = Depends(get_current_user),
                       db: AsyncSession = Depends(get_db)):
    product = await product_crud.get_by_id(db, product_id)
    if not product:
        raise HTTPException(status_code=404, detail="商品不存在")
    detail = ProductDetail.model_validate(product)
    detail.category_name = product.category.name if product.category else None
    # Calculate days until out of stock
    if product.monthly_consumption > 0:
        detail.days_until_out_of_stock = round(product.current_stock / (product.monthly_consumption / 30), 1)
    # Get best price
    plans = product.purchase_plans
    if plans:
        best = min(plans, key=lambda p: p.price if p.price else 0)
        detail.best_channel = best.channel_name
        detail.best_price = best.price
    return detail


@router.put("/{product_id}", response_model=ProductResponse)
async def update_product(product_id: str, data: ProductUpdate,
                          current_user: User = Depends(get_current_user),
                          db: AsyncSession = Depends(get_db)):
    product = await product_crud.update(db, product_id, **data.model_dump(exclude_none=True))
    if not product:
        raise HTTPException(status_code=404, detail="商品不存在")
    try:
        await sync_to_meili(product, "")
    except Exception:
        pass
    return ProductResponse.model_validate(product)


@router.delete("/{product_id}")
async def delete_product(product_id: str, current_user: User = Depends(get_current_user),
                          db: AsyncSession = Depends(get_db)):
    success = await product_crud.delete(db, product_id)
    if not success:
        raise HTTPException(status_code=404, detail="商品不存在")
    try:
        await remove_from_meili(product_id)
    except Exception:
        pass
    return {"message": "商品已删除"}


@router.get("/low-stock/family/{family_id}", response_model=list[ProductResponse])
async def get_low_stock_products(family_id: str, threshold_days: float = Query(3, ge=1),
                                  current_user: User = Depends(get_current_user),
                                  db: AsyncSession = Depends(get_db)):
    if not await family_member_crud.is_member(db, family_id, current_user.id):
        raise HTTPException(status_code=403, detail="不是家庭成员")
    products = await product_crud.get_low_stock_products(db, family_id, threshold_days)
    return [ProductResponse.model_validate(p) for p in products]


@router.post("/{product_id}/plans", response_model=PurchasePlanResponse, status_code=201)
async def create_purchase_plan(product_id: str, data: PurchasePlanCreate,
                                current_user: User = Depends(get_current_user),
                                db: AsyncSession = Depends(get_db)):
    plan = await purchase_plan_crud.create(db, product_id, **data.model_dump())
    return PurchasePlanResponse.model_validate(plan)


@router.put("/plans/{plan_id}", response_model=PurchasePlanResponse)
async def update_purchase_plan(plan_id: str, data: PurchasePlanUpdate,
                                current_user: User = Depends(get_current_user),
                                db: AsyncSession = Depends(get_db)):
    plan = await purchase_plan_crud.update(db, plan_id, **data.model_dump(exclude_none=True))
    if not plan:
        raise HTTPException(status_code=404, detail="采购方案不存在")
    return PurchasePlanResponse.model_validate(plan)


@router.delete("/plans/{plan_id}")
async def delete_purchase_plan(plan_id: str, current_user: User = Depends(get_current_user),
                                db: AsyncSession = Depends(get_db)):
    success = await purchase_plan_crud.delete(db, plan_id)
    if not success:
        raise HTTPException(status_code=404, detail="采购方案不存在")
    return {"message": "采购方案已删除"}


@router.put("/{product_id}/plans/{plan_id}/set-primary")
async def set_primary_plan(product_id: str, plan_id: str,
                            current_user: User = Depends(get_current_user),
                            db: AsyncSession = Depends(get_db)):
    await purchase_plan_crud.set_primary(db, product_id, plan_id)
    return {"message": "已设为首选方案"}
