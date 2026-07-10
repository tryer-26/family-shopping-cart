 from fastapi import APIRouter, Depends, HTTPException, Query, status
 from sqlalchemy.ext.asyncio import AsyncSession
 
 from app.database import get_db
 from app.dependencies import get_current_user
 from app.models.user import User
 from app.schemas.shopping_list import (
     ShoppingListItemCreate, ShoppingListItemUpdate, ShoppingListItemResponse,
     ShoppingListBatchAdd, ShoppingListStats,
 )
 from app.crud.shopping_list import shopping_list_crud
 from app.crud.family import family_member_crud
 from app.utils.pagination import PaginationParams, PaginatedResult
 
 router = APIRouter(prefix="/shopping-list", tags=["采购清单"])
 
 
 @router.post("/family/{family_id}", response_model=ShoppingListItemResponse, status_code=201)
 async def add_item(family_id: str, data: ShoppingListItemCreate,
                     current_user: User = Depends(get_current_user),
                     db: AsyncSession = Depends(get_db)):
     if not await family_member_crud.is_member(db, family_id, current_user.id):
         raise HTTPException(status_code=403, detail="不是家庭成员")
     item = await shopping_list_crud.add_item(
         db, family_id, data.product_id, current_user.id,
         data.quantity, data.purchase_plan_id, data.notes,
     )
     return await _enrich_item(db, item)
 
 
 @router.post("/family/{family_id}/batch", response_model=list[ShoppingListItemResponse], status_code=201)
 async def batch_add(family_id: str, data: ShoppingListBatchAdd,
                      current_user: User = Depends(get_current_user),
                      db: AsyncSession = Depends(get_db)):
     if not await family_member_crud.is_member(db, family_id, current_user.id):
         raise HTTPException(status_code=403, detail="不是家庭成员")
     items_data = [d.model_dump() for d in data.items]
     items = await shopping_list_crud.batch_add(db, family_id, current_user.id, items_data)
     return [await _enrich_item(db, item) for item in items]
 
 
 @router.get("/family/{family_id}", response_model=PaginatedResult)
 async def list_items(family_id: str, status: str | None = Query(None),
                       page: int = Query(1, ge=1), page_size: int = Query(50, ge=1, le=200),
                       current_user: User = Depends(get_current_user),
                       db: AsyncSession = Depends(get_db)):
     if not await family_member_crud.is_member(db, family_id, current_user.id):
         raise HTTPException(status_code=403, detail="不是家庭成员")
     from app.models.shopping_list import ShoppingItemStatus
     status_enum = ShoppingItemStatus(status) if status else None
     params = PaginationParams(page, page_size)
     result = await shopping_list_crud.get_family_items(db, family_id, status_enum, params)
     result.items = [await _enrich_item(db, item) for item in result.items]
     return result
 
 
 @router.put("/{item_id}", response_model=ShoppingListItemResponse)
 async def update_item(item_id: str, data: ShoppingListItemUpdate,
                        current_user: User = Depends(get_current_user),
                        db: AsyncSession = Depends(get_db)):
     item = await shopping_list_crud.update_item(db, item_id, **data.model_dump(exclude_none=True))
     if not item:
         raise HTTPException(status_code=404, detail="清单项不存在")
     return await _enrich_item(db, item)
 
 
 @router.post("/{item_id}/purchase", response_model=ShoppingListItemResponse)
 async def mark_purchased(item_id: str, actual_price: float | None = Query(None),
                           current_user: User = Depends(get_current_user),
                           db: AsyncSession = Depends(get_db)):
     item = await shopping_list_crud.mark_purchased(db, item_id, current_user.id, actual_price)
     if not item:
         raise HTTPException(status_code=404, detail="清单项不存在")
     return await _enrich_item(db, item)
 
 
 @router.delete("/{item_id}")
 async def delete_item(item_id: str, current_user: User = Depends(get_current_user),
                        db: AsyncSession = Depends(get_db)):
     success = await shopping_list_crud.delete_item(db, item_id)
     if not success:
         raise HTTPException(status_code=404, detail="清单项不存在")
     return {"message": "已从清单移除"}
 
 
 @router.delete("/family/{family_id}/clear-purchased")
 async def clear_purchased(family_id: str, current_user: User = Depends(get_current_user),
                            db: AsyncSession = Depends(get_db)):
     if not await family_member_crud.is_member(db, family_id, current_user.id):
         raise HTTPException(status_code=403, detail="不是家庭成员")
     await shopping_list_crud.clear_purchased(db, family_id)
     return {"message": "已清空已购项目"}
 
 
 @router.get("/family/{family_id}/stats", response_model=ShoppingListStats)
 async def get_shopping_stats(family_id: str, current_user: User = Depends(get_current_user),
                               db: AsyncSession = Depends(get_db)):
     if not await family_member_crud.is_member(db, family_id, current_user.id):
         raise HTTPException(status_code=403, detail="不是家庭成员")
     stats = await shopping_list_crud.get_stats(db, family_id)
     return ShoppingListStats(**stats)
 
 
 async def _enrich_item(db: AsyncSession, item) -> ShoppingListItemResponse:
     """Enrich a shopping list item with product and plan details."""
     from sqlalchemy import select
     from app.models.product import Product, PurchasePlan
     from app.models.category import Category
     from app.models.user import User
     
     resp = ShoppingListItemResponse(
         id=item.id, family_id=item.family_id, product_id=item.product_id,
         purchase_plan_id=item.purchase_plan_id, quantity=item.quantity,
         estimated_price=item.estimated_price, actual_price=item.actual_price,
         status=item.status, added_by=item.added_by, purchased_by=item.purchased_by,
         notes=item.notes, created_at=item.created_at,
     )
     
     # Get product info
     if item.product_id:
         result = await db.execute(
             select(Product, Category.name).join(Category, Product.category_id == Category.id)
             .where(Product.id == item.product_id)
         )
         row = result.one_or_none()
         if row:
             product, cat_name = row
             resp.product_name = product.name
             resp.product_unit = product.unit
             resp.category_name = cat_name
     
     # Get purchase plan info
     if item.purchase_plan_id:
         result = await db.execute(
             select(PurchasePlan).where(PurchasePlan.id == item.purchase_plan_id)
         )
         plan = result.scalar_one_or_none()
         if plan:
             resp.plan_channel_name = plan.channel_name
             resp.plan_price = plan.price
     
     # Get user names
     if item.added_by:
         result = await db.execute(select(User.username).where(User.id == item.added_by))
         user_row = result.one_or_none()
         if user_row:
             resp.added_by_name = user_row[0]
     
     return resp
