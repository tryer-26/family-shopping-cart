from fastapi import APIRouter, Depends, HTTPException, Query
from sqlalchemy.ext.asyncio import AsyncSession

from app.database import get_db
from app.dependencies import get_current_user
from app.models.user import User
from app.schemas.price import (
    PriceChannelCreate, PriceChannelUpdate, PriceChannelResponse,
    PriceHistoryResponse, BestPriceResponse,
)
from app.crud.price import price_channel_crud, price_history_crud
from app.crud.product import purchase_plan_crud
from app.crud.family import family_member_crud
from app.tasks.price_scraper import scrape_product_price

router = APIRouter(prefix="/prices", tags=["价格管理"])


@router.post("/channels/plan/{purchase_plan_id}", response_model=PriceChannelResponse, status_code=201)
async def create_price_channel(purchase_plan_id: str, data: PriceChannelCreate,
                                current_user: User = Depends(get_current_user),
                                db: AsyncSession = Depends(get_db)):
    pc = await price_channel_crud.create(db, purchase_plan_id, **data.model_dump())
    return PriceChannelResponse.model_validate(pc)


@router.get("/channels/plan/{purchase_plan_id}", response_model=list[PriceChannelResponse])
async def list_price_channels(purchase_plan_id: str,
                               current_user: User = Depends(get_current_user),
                               db: AsyncSession = Depends(get_db)):
    channels = await price_channel_crud.get_by_plan(db, purchase_plan_id)
    return [PriceChannelResponse.model_validate(c) for c in channels]


@router.put("/channels/{channel_id}", response_model=PriceChannelResponse)
async def update_price_channel(channel_id: str, data: PriceChannelUpdate,
                                current_user: User = Depends(get_current_user),
                                db: AsyncSession = Depends(get_db)):
    pc = await price_channel_crud.update(db, channel_id, **data.model_dump(exclude_none=True))
    if not pc:
        raise HTTPException(status_code=404, detail="价格渠道不存在")
    return PriceChannelResponse.model_validate(pc)


@router.delete("/channels/{channel_id}")
async def delete_price_channel(channel_id: str,
                                current_user: User = Depends(get_current_user),
                                db: AsyncSession = Depends(get_db)):
    success = await price_channel_crud.delete(db, channel_id)
    if not success:
        raise HTTPException(status_code=404, detail="价格渠道不存在")
    return {"message": "价格渠道已删除"}


@router.get("/history/{product_id}", response_model=list[PriceHistoryResponse])
async def get_price_history(product_id: str, days: int = Query(90, ge=7, le=365),
                             current_user: User = Depends(get_current_user),
                             db: AsyncSession = Depends(get_db)):
    history = await price_history_crud.get_history(db, product_id, days)
    return [PriceHistoryResponse.model_validate(h) for h in history]


@router.get("/best/{product_id}", response_model=BestPriceResponse | None)
async def get_best_price(product_id: str, current_user: User = Depends(get_current_user),
                          db: AsyncSession = Depends(get_db)):
    best = await price_channel_crud.get_best_price_for_product(db, product_id)
    if not best:
        return None
    return BestPriceResponse(**best)


@router.post("/scrape/{product_id}")
async def trigger_scrape(product_id: str, url: str = Query(..., description="商品链接"),
                          current_user: User = Depends(get_current_user)):
    """
    Trigger a price scrape for a single product.
    DISCLAIMER: For personal/family use only.
    """
    task = scrape_product_price.delay(product_id, url)
    return {"task_id": task.id, "message": "价格抓取任务已提交"}


@router.get("/best-for-family/{family_id}", response_model=list[BestPriceResponse])
async def get_best_prices_for_family(family_id: str,
                                      current_user: User = Depends(get_current_user),
                                      db: AsyncSession = Depends(get_db)):
    if not await family_member_crud.is_member(db, family_id, current_user.id):
        raise HTTPException(status_code=403, detail="不是家庭成员")
    from app.models.product import Product, PurchasePlan
    from sqlalchemy import select
    result = await db.execute(
        select(Product.id, Product.name, PurchasePlan.channel_name,
               PurchasePlan.price, PurchasePlan.product_url)
        .join(PurchasePlan, Product.id == PurchasePlan.product_id)
        .where(Product.family_id == family_id, Product.is_active == True, PurchasePlan.is_primary == True)
    )
    items = []
    for row in result.all():
        items.append(BestPriceResponse(
            product_id=row[0], product_name=row[1],
            channel_name=row[2] or "", final_price=row[3] or 0,
            product_url=row[4],
        ))
    return items
