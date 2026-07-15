from math import ceil
from pydantic import BaseModel, Field
from sqlalchemy import select, func
from sqlalchemy.ext.asyncio import AsyncSession


class PaginationParams:
    def __init__(self, page: int = 1, page_size: int = 20):
        self.page = max(1, page)
        self.page_size = min(100, max(1, page_size))

    @property
    def offset(self) -> int:
        return (self.page - 1) * self.page_size

    @property
    def limit(self) -> int:
        return self.page_size


class PaginatedResult(BaseModel):
    items: list = Field(default_factory=list)
    total: int = 0
    page: int = 1
    page_size: int = 20
    total_pages: int = 0
    model_config = {"from_attributes": True}


async def paginate(db: AsyncSession, stmt, params: PaginationParams) -> PaginatedResult:
    count_stmt = select(func.count()).select_from(stmt.subquery())
    count_result = await db.execute(count_stmt)
    total = count_result.scalar_one()
    total_pages = ceil(total / params.page_size) if total > 0 else 0
    query = stmt.offset(params.offset).limit(params.limit)
    result = await db.execute(query)
    items = list(result.scalars().all())
    return PaginatedResult(
        items=items, total=total, page=params.page,
        page_size=params.page_size, total_pages=total_pages,
    )
