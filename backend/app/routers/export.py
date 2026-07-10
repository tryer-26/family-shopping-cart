 from fastapi import APIRouter, Depends, HTTPException, Query
 from fastapi.responses import StreamingResponse, Response
 from sqlalchemy.ext.asyncio import AsyncSession
 from sqlalchemy import select
 import io
 
 from app.database import get_db
 from app.dependencies import get_current_user
 from app.models.user import User
 from app.crud.family import family_member_crud
 from app.crud.shopping_list import shopping_list_crud
 from app.services.export import export_to_csv, export_to_excel, export_to_pdf
 
 router = APIRouter(prefix="/export", tags=["导出"])
 
 
 @router.get("/shopping-list/{family_id}")
 async def export_shopping_list(
     family_id: str,
     fmt: str = Query("csv", regex="^(csv|xlsx|pdf)$", description="导出格式"),
     status: str | None = Query(None, description="筛选状态"),
     current_user: User = Depends(get_current_user),
     db: AsyncSession = Depends(get_db),
 ):
     if not await family_member_crud.is_member(db, family_id, current_user.id):
         raise HTTPException(status_code=403, detail="不是家庭成员")
     
     from app.models.shopping_list import ShoppingItemStatus
     status_enum = ShoppingItemStatus(status) if status else None
     result = await shopping_list_crud.get_family_items(db, family_id, status_enum)
     
     # Enrich items with product/category info
     enriched = []
     for item in result.items:
         from app.models.product import Product, PurchasePlan
         from app.models.category import Category
         prod_result = await db.execute(
             select(Product, Category.name)
             .join(Category, Product.category_id == Category.id)
             .where(Product.id == item.product_id)
         )
         row = prod_result.one_or_none()
         product = row[0] if row else None
         cat_name = row[1] if row else ""
         enriched.append({
             "category_name": cat_name,
             "product_name": product.name if product else "",
             "brand": product.brand if product else "",
             "specification": product.specification if product else "",
             "quantity": item.quantity,
             "unit": product.unit if product else "个",
             "best_channel": "",
             "best_price": str(item.estimated_price or ""),
             "product_url": "",
             "notes": item.notes or "",
         })
     
     if fmt == "csv":
         data = export_to_csv(enriched)
         media_type = "text/csv"
         filename = f"shopping_list_{family_id}.csv"
     elif fmt == "xlsx":
         data = export_to_excel(enriched)
         media_type = "application/vnd.openxmlformats-officedocument.spreadsheetml.sheet"
         filename = f"shopping_list_{family_id}.xlsx"
     else:
         data = export_to_pdf(enriched)
         media_type = "application/pdf"
         filename = f"shopping_list_{family_id}.pdf"
     
     return Response(content=data, media_type=media_type, headers={
         "Content-Disposition": f'attachment; filename="{filename}"',
     })
 
 
 @router.get("/backup/{family_id}")
 async def export_backup(family_id: str, current_user: User = Depends(get_current_user),
                          db: AsyncSession = Depends(get_db)):
     """Export all family data as JSON backup."""
     if not await family_member_crud.is_member(db, family_id, current_user.id):
         raise HTTPException(status_code=403, detail="不是家庭成员")
     
     import json
     from app.models.product import Product, PurchasePlan
     from app.models.category import Category
     from app.models.coupon import Coupon
     from app.models.shopping_list import ShoppingListItem
     
     backup = {"family_id": family_id, "exported_at": str(datetime.now(timezone.utc))}
     
     for model_cls, key in [
         (Category, "categories"), (Product, "products"),
         (Coupon, "coupons"), (ShoppingListItem, "shopping_list"),
     ]:
         result = await db.execute(select(model_cls).where(model_cls.family_id == family_id))
         rows = result.scalars().all()
         backup[key] = [{c.name: getattr(r, c.name) for c in model_cls.__table__.columns} for r in rows]
     
     from datetime import datetime, timezone
     data = json.dumps(backup, ensure_ascii=False, default=str).encode("utf-8")
     return Response(content=data, media_type="application/json", headers={
         "Content-Disposition": f'attachment; filename="hpms_backup_{family_id}.json"',
     })
