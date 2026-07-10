import logging
from datetime import datetime, timezone, timedelta
from calendar import monthrange

from sqlalchemy import select, func, and_, case
from sqlalchemy.ext.asyncio import AsyncSession

from app.models.shopping_list import ShoppingListItem, ShoppingItemStatus
from app.models.product import Product, PurchasePlan
from app.models.category import Category

logger = logging.getLogger(__name__)


async def get_monthly_report(db: AsyncSession, family_id: str, year: int, month: int) -> dict:
    """Generate monthly statistics report."""
    start_date = datetime(year, month, 1, tzinfo=timezone.utc)
    end_date = datetime(year, month, monthrange(year, month)[1], 23, 59, 59, tzinfo=timezone.utc)

    # Total spending
    total_result = await db.execute(
        select(func.sum(ShoppingListItem.actual_price))
        .where(
            and_(
                ShoppingListItem.family_id == family_id,
                ShoppingListItem.status == ShoppingItemStatus.PURCHASED,
                ShoppingListItem.updated_at >= start_date,
                ShoppingListItem.updated_at <= end_date,
            )
        )
    )
    total_spending = total_result.scalar_one() or 0

    # Category breakdown
    cat_result = await db.execute(
        select(
            Category.name,
            func.sum(ShoppingListItem.actual_price).label("total"),
            func.count(ShoppingListItem.id).label("count"),
        )
        .join(Product, ShoppingListItem.product_id == Product.id)
        .join(Category, Product.category_id == Category.id)
        .where(
            and_(
                ShoppingListItem.family_id == family_id,
                ShoppingListItem.status == ShoppingItemStatus.PURCHASED,
                ShoppingListItem.updated_at >= start_date,
                ShoppingListItem.updated_at <= end_date,
            )
        )
        .group_by(Category.name)
    )
    category_breakdown = []
    for row in cat_result.all():
        category_breakdown.append({
            "name": row[0],
            "total": float(row[1] or 0),
            "count": row[2] or 0,
        })

    # Channel breakdown
    channel_result = await db.execute(
        select(
            PurchasePlan.channel_name,
            func.sum(ShoppingListItem.actual_price).label("total"),
            func.count(ShoppingListItem.id).label("count"),
        )
        .join(Product, ShoppingListItem.product_id == Product.id)
        .join(PurchasePlan, Product.id == PurchasePlan.product_id)
        .where(
            and_(
                ShoppingListItem.family_id == family_id,
                ShoppingListItem.status == ShoppingItemStatus.PURCHASED,
                ShoppingListItem.updated_at >= start_date,
                ShoppingListItem.updated_at <= end_date,
            )
        )
        .group_by(PurchasePlan.channel_name)
    )
    channel_breakdown = []
    for row in channel_result.all():
        channel_breakdown.append({
            "channel": row[0],
            "total": float(row[1] or 0),
            "count": row[2] or 0,
        })

    return {
        "year": year,
        "month": month,
        "total_spending": float(total_spending),
        "total_items": sum(b["count"] for b in category_breakdown),
        "category_breakdown": category_breakdown,
        "channel_breakdown": channel_breakdown,
    }


async def get_dashboard_stats(db: AsyncSession, family_id: str) -> dict:
    """Get dashboard summary statistics."""
    # Low stock count (items with <= 3 days of consumption left)
    low_stock_result = await db.execute(
        select(func.count(Product.id))
        .where(
            and_(
                Product.family_id == family_id,
                Product.is_active == True,
                Product.monthly_consumption > 0,
                Product.current_stock / (func.nullif(Product.monthly_consumption / 30, 0)) <= 3,
            )
        )
    )
    low_stock_count = low_stock_result.scalar_one() or 0

    # Pending shopping items
    pending_result = await db.execute(
        select(func.count(ShoppingListItem.id))
        .where(
            and_(
                ShoppingListItem.family_id == family_id,
                ShoppingListItem.status == ShoppingItemStatus.PENDING,
            )
        )
    )
    pending_count = pending_result.scalar_one() or 0

    # Total products
    product_result = await db.execute(
        select(func.count(Product.id))
        .where(and_(Product.family_id == family_id, Product.is_active == True))
    )
    total_products = product_result.scalar_one() or 0

    return {
        "low_stock_count": low_stock_count,
        "pending_count": pending_count,
        "total_products": total_products,
    }


async def get_yearly_comparison(db: AsyncSession, family_id: str, year: int) -> list[dict]:
    """Get monthly comparison for a given year."""
    monthly_data = []
    for month in range(1, 13):
        report = await get_monthly_report(db, family_id, year, month)
        monthly_data.append({
            "month": month,
            "total_spending": report["total_spending"],
            "total_items": report["total_items"],
        })
    return monthly_data
