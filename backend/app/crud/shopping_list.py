from sqlalchemy import select, and_, func
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.orm import joinedload

from app.models.shopping_list import ShoppingListItem, ShoppingItemStatus
from app.models.product import Product, PurchasePlan
from app.utils.pagination import paginate, PaginationParams, PaginatedResult


class ShoppingListCRUD:
    async def add_item(self, db: AsyncSession, family_id: str, product_id: str,
                       added_by: str, quantity: float = 1, purchase_plan_id: str | None = None,
                       notes: str | None = None) -> ShoppingListItem:
        item = ShoppingListItem(
            family_id=family_id, product_id=product_id, added_by=added_by,
            quantity=quantity, purchase_plan_id=purchase_plan_id, notes=notes,
        )
        db.add(item)
        await db.flush()
        await db.refresh(item)
        return item

    async def batch_add(self, db: AsyncSession, family_id: str, added_by: str,
                        items: list[dict]) -> list[ShoppingListItem]:
        created = []
        for item_data in items:
            item = ShoppingListItem(
                family_id=family_id, product_id=item_data["product_id"],
                added_by=added_by, quantity=item_data.get("quantity", 1),
                purchase_plan_id=item_data.get("purchase_plan_id"),
                notes=item_data.get("notes"),
            )
            db.add(item)
            created.append(item)
        await db.flush()
        for item in created:
            await db.refresh(item)
        return created

    async def get_family_items(self, db: AsyncSession, family_id: str,
                               status: ShoppingItemStatus | None = None,
                               params: PaginationParams | None = None) -> PaginatedResult:
        stmt = select(ShoppingListItem).options(
            joinedload(ShoppingListItem.product),
            joinedload(ShoppingListItem.purchase_plan),
        ).where(ShoppingListItem.family_id == family_id)

        if status:
            stmt = stmt.where(ShoppingListItem.status == status)

        stmt = stmt.order_by(ShoppingListItem.created_at.desc())

        if params:
            return await paginate(db, stmt, params)
        result = await db.execute(stmt)
        items = list(result.unique().scalars().all())
        return PaginatedResult(items=items, total=len(items), page=1, page_size=len(items), total_pages=1)

    async def update_item(self, db: AsyncSession, item_id: str, **kwargs) -> ShoppingListItem | None:
        result = await db.execute(select(ShoppingListItem).where(ShoppingListItem.id == item_id))
        item = result.scalar_one_or_none()
        if not item:
            return None
        for key, value in kwargs.items():
            if value is not None and hasattr(item, key):
                setattr(item, key, value)
        await db.flush()
        await db.refresh(item)
        return item

    async def mark_purchased(self, db: AsyncSession, item_id: str, purchased_by: str,
                             actual_price: float | None = None) -> ShoppingListItem | None:
        result = await db.execute(select(ShoppingListItem).where(ShoppingListItem.id == item_id))
        item = result.scalar_one_or_none()
        if not item:
            return None
        item.status = ShoppingItemStatus.PURCHASED
        item.purchased_by = purchased_by
        if actual_price is not None:
            item.actual_price = actual_price
        await db.flush()
        await db.refresh(item)
        return item

    async def delete_item(self, db: AsyncSession, item_id: str) -> bool:
        result = await db.execute(select(ShoppingListItem).where(ShoppingListItem.id == item_id))
        item = result.scalar_one_or_none()
        if not item:
            return False
        await db.delete(item)
        await db.flush()
        return True

    async def clear_purchased(self, db: AsyncSession, family_id: str):
        result = await db.execute(
            select(ShoppingListItem).where(
                and_(
                    ShoppingListItem.family_id == family_id,
                    ShoppingListItem.status == ShoppingItemStatus.PURCHASED,
                )
            )
        )
        items = list(result.scalars().all())
        for item in items:
            await db.delete(item)
        await db.flush()

    async def get_stats(self, db: AsyncSession, family_id: str) -> dict:
        result = await db.execute(
            select(
                func.count(ShoppingListItem.id),
                func.sum(case((ShoppingListItem.status == ShoppingItemStatus.PENDING, 1), else_=0)),
                func.sum(case((ShoppingListItem.status == ShoppingItemStatus.PURCHASED, 1), else_=0)),
                func.sum(case((ShoppingListItem.status == ShoppingItemStatus.PENDING, ShoppingListItem.estimated_price), else_=0)),
                func.sum(case((ShoppingListItem.status == ShoppingItemStatus.PURCHASED, ShoppingListItem.actual_price), else_=0)),
            ).where(ShoppingListItem.family_id == family_id)
        )
        row = result.one()
        from sqlalchemy import case
        # Re-query with proper case
        return {
            "total_items": row[0] or 0,
            "pending_count": row[1] or 0,
            "purchased_count": row[2] or 0,
            "estimated_total": float(row[3] or 0),
            "actual_total": float(row[4] or 0),
        }


shopping_list_crud = ShoppingListCRUD()
