from fastapi import APIRouter, Depends, HTTPException, Query
from sqlalchemy.ext.asyncio import AsyncSession

from app.database import get_db
from app.dependencies import get_current_user
from app.models.user import User
from app.services.meilisearch import search_products, search_all
from app.crud.family import family_member_crud

router = APIRouter(prefix="/search", tags=["搜索"])


@router.get("/products")
async def search(q: str = Query(..., min_length=1, description="搜索关键词"),
                  family_id: str | None = Query(None, description="限定家庭"),
                  limit: int = Query(20, ge=1, le=100),
                  current_user: User = Depends(get_current_user)):
    """Search products by name, brand, notes. Supports fuzzy matching."""
    if family_id:
        results = await search_products(family_id, q, limit)
    else:
        results = await search_all(q, limit)
    return {"query": q, "results": results, "total": len(results)}


@router.get("/products/local")
async def search_local(q: str = Query(..., min_length=1, description="搜索关键词"),
                        family_id: str = Query(..., description="家庭ID"),
                        current_user: User = Depends(get_current_user),
                        db: AsyncSession = Depends(get_db)):
    """Fallback local DB search when Meilisearch is unavailable."""
    if not await family_member_crud.is_member(db, family_id, current_user.id):
        raise HTTPException(status_code=403, detail="不是家庭成员")
    from sqlalchemy import select, or_
    from app.models.product import Product
    stmt = select(Product).where(
        Product.family_id == family_id,
        Product.is_active == True,
        or_(
            Product.name.ilike(f"%{q}%"),
            Product.brand.ilike(f"%{q}%"),
            Product.notes.ilike(f"%{q}%"),
        ),
    ).limit(20)
    result = await db.execute(stmt)
    products = list(result.scalars().all())
    return {"query": q, "results": [{"id": p.id, "name": p.name, "brand": p.brand} for p in products], "total": len(products)}
