from sqlalchemy import select, and_, or_
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.orm import joinedload

from app.models.product import Product, PurchasePlan
from app.models.category import Category
from app.utils.pagination import paginate, PaginationParams, PaginatedResult


class ProductCRUD:
    async def create(self, db: AsyncSession, family_id: str, category_id: str, name: str,
                     **kwargs) -> Product:
        product = Product(family_id=family_id, category_id=category_id, name=name, **kwargs)
        db.add(product)
        await db.flush()
        await db.refresh(product)
        return product

    async def get_by_id(self, db: AsyncSession, product_id: str) -> Product | None:
        result = await db.execute(
            select(Product).options(
                joinedload(Product.purchase_plans),
                joinedload(Product.category),
            ).where(Product.id == product_id)
        )
        return result.unique().scalar_one_or_none()

    async def get_family_products(self, db: AsyncSession, family_id: str, category_id: str | None = None,
                                  is_blacklisted: bool | None = None, keyword: str | None = None,
                                  params: PaginationParams | None = None) -> PaginatedResult:
        stmt = select(Product).options(
            joinedload(Product.purchase_plans), joinedload(Product.category)
        ).where(Product.family_id == family_id, Product.is_active == True)

        if category_id:
            stmt = stmt.where(Product.category_id == category_id)
        if is_blacklisted is not None:
            stmt = stmt.where(Product.is_blacklisted == is_blacklisted)
        if keyword:
            stmt = stmt.where(
                or_(Product.name.ilike(f"%{keyword}%"), Product.brand.ilike(f"%{keyword}%"))
            )

        stmt = stmt.order_by(Product.updated_at.desc())
        if params:
            return await paginate(db, stmt, params)
        result = await db.execute(stmt)
        items = list(result.unique().scalars().all())
        return PaginatedResult(items=items, total=len(items), page=1, page_size=len(items), total_pages=1)

    async def update(self, db: AsyncSession, product_id: str, **kwargs) -> Product | None:
        product = await self.get_by_id(db, product_id)
        if not product:
            return None
        for key, value in kwargs.items():
            if value is not None and hasattr(product, key):
                setattr(product, key, value)
        await db.flush()
        await db.refresh(product)
        return product

    async def delete(self, db: AsyncSession, product_id: str) -> bool:
        product = await self.get_by_id(db, product_id)
        if not product:
            return False
        await db.delete(product)
        await db.flush()
        return True

    async def get_low_stock_products(self, db: AsyncSession, family_id: str, threshold_days: float = 3) -> list[Product]:
        result = await db.execute(
            select(Product).where(
                and_(
                    Product.family_id == family_id,
                    Product.is_active == True,
                    Product.monthly_consumption > 0,
                    Product.current_stock / (Product.monthly_consumption / 30) <= threshold_days,
                )
            ).order_by((Product.current_stock / (Product.monthly_consumption / 30)).asc())
        )
        return list(result.scalars().all())

    async def increment_repurchase(self, db: AsyncSession, product_id: str):
        product = await self.get_by_id(db, product_id)
        if product:
            product.repurchase_count = (product.repurchase_count or 0) + 1
            await db.flush()


class PurchasePlanCRUD:
    async def create(self, db: AsyncSession, product_id: str, **kwargs) -> PurchasePlan:
        plan = PurchasePlan(product_id=product_id, **kwargs)
        db.add(plan)
        await db.flush()
        await db.refresh(plan)
        return plan

    async def get_by_id(self, db: AsyncSession, plan_id: str) -> PurchasePlan | None:
        result = await db.execute(select(PurchasePlan).where(PurchasePlan.id == plan_id))
        return result.scalar_one_or_none()

    async def get_by_product(self, db: AsyncSession, product_id: str) -> list[PurchasePlan]:
        result = await db.execute(
            select(PurchasePlan).where(PurchasePlan.product_id == product_id)
            .order_by(PurchasePlan.is_primary.desc(), PurchasePlan.price.asc())
        )
        return list(result.scalars().all())

    async def update(self, db: AsyncSession, plan_id: str, **kwargs) -> PurchasePlan | None:
        plan = await self.get_by_id(db, plan_id)
        if not plan:
            return None
        for key, value in kwargs.items():
            if value is not None and hasattr(plan, key):
                setattr(plan, key, value)
        await db.flush()
        await db.refresh(plan)
        return plan

    async def delete(self, db: AsyncSession, plan_id: str) -> bool:
        plan = await self.get_by_id(db, plan_id)
        if not plan:
            return False
        await db.delete(plan)
        await db.flush()
        return True

    async def set_primary(self, db: AsyncSession, product_id: str, plan_id: str):
        plans = await self.get_by_product(db, product_id)
        for plan in plans:
            plan.is_primary = (plan.id == plan_id)
        await db.flush()


product_crud = ProductCRUD()
purchase_plan_crud = PurchasePlanCRUD()
