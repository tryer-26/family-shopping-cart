from sqlalchemy import select, and_
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.orm import joinedload

from app.models.category import Category
from app.utils.pagination import paginate, PaginationParams, PaginatedResult


class CategoryCRUD:
   async def create(self, db: AsyncSession, family_id: str, name: str, parent_id: str | None = None,
                    emoji: str | None = None, sort_order: int = 0) -> Category:
       category = Category(family_id=family_id, name=name, parent_id=parent_id, emoji=emoji, sort_order=sort_order)
       db.add(category)
       await db.flush()
       await db.refresh(category)
       return category

   async def get_by_id(self, db: AsyncSession, category_id: str) -> Category | None:
       result = await db.execute(select(Category).where(Category.id == category_id))
       return result.scalar_one_or_none()

   async def get_tree(self, db: AsyncSession, family_id: str) -> list[Category]:
       result = await db.execute(
           select(Category).where(
               and_(Category.family_id == family_id, Category.is_active == True)
           ).order_by(Category.sort_order, Category.name)
       )
       return list(result.scalars().all())

   async def update(self, db: AsyncSession, category_id: str, **kwargs) -> Category | None:
       cat = await self.get_by_id(db, category_id)
       if not cat:
           return None
       for key, value in kwargs.items():
           if value is not None and hasattr(cat, key):
               setattr(cat, key, value)
       await db.flush()
       await db.refresh(cat)
       return cat

   async def delete(self, db: AsyncSession, category_id: str) -> bool:
       cat = await self.get_by_id(db, category_id)
       if not cat:
           return False
       await db.delete(cat)
       await db.flush()
       return True

   async def paginate(self, db: AsyncSession, family_id: str, params: PaginationParams) -> PaginatedResult:
       stmt = select(Category).where(Category.family_id == family_id).order_by(Category.sort_order, Category.name)
       return await paginate(db, stmt, params)


category_crud = CategoryCRUD()
