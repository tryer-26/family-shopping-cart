 from fastapi import APIRouter, Depends, HTTPException, status
 from sqlalchemy.ext.asyncio import AsyncSession
 
 from app.database import get_db
 from app.dependencies import get_current_user
 from app.models.user import User
 from app.schemas.category import CategoryCreate, CategoryUpdate, CategoryResponse, CategoryTreeNode
 from app.crud.category import category_crud
 from app.crud.family import family_member_crud
 
 router = APIRouter(prefix="/categories", tags=["分类管理"])
 
 DEFAULT_CATEGORIES = [
     {"name": "洗护清洁", "emoji": "🧹", "sort_order": 1},
     {"name": "食品零食", "emoji": "🍜", "sort_order": 2},
     {"name": "宠物用品", "emoji": "🐾", "sort_order": 3},
     {"name": "日用百货", "emoji": "🏠", "sort_order": 4},
     {"name": "厨卫耗材", "emoji": "🍳", "sort_order": 5},
     {"name": "家居用品", "emoji": "🛋", "sort_order": 6},
 ]
 
 
 @router.post("", response_model=CategoryResponse, status_code=status.HTTP_201_CREATED)
 async def create_category(data: CategoryCreate, current_user: User = Depends(get_current_user),
                            db: AsyncSession = Depends(get_db)):
     # Get user's first family or require family_id
     families = await family_member_crud.get_members(db, "family_id")
     # Assume family_id comes from header or query
     raise HTTPException(status_code=501, detail="请使用带family_id的接口")
 
 
 @router.post("/family/{family_id}", response_model=CategoryResponse, status_code=status.HTTP_201_CREATED)
 async def create_category_in_family(family_id: str, data: CategoryCreate,
                                      current_user: User = Depends(get_current_user),
                                      db: AsyncSession = Depends(get_db)):
     if not await family_member_crud.is_member(db, family_id, current_user.id):
         raise HTTPException(status_code=403, detail="不是家庭成员")
     cat = await category_crud.create(db, family_id, data.name, data.parent_id, data.emoji, data.sort_order)
     return CategoryResponse.model_validate(cat)
 
 
 @router.get("/family/{family_id}", response_model=list[CategoryTreeNode])
 async def get_category_tree(family_id: str, current_user: User = Depends(get_current_user),
                              db: AsyncSession = Depends(get_db)):
     if not await family_member_crud.is_member(db, family_id, current_user.id):
         raise HTTPException(status_code=403, detail="不是家庭成员")
     categories = await category_crud.get_tree(db, family_id)
     # Build tree
     cat_map = {c.id: CategoryTreeNode.model_validate(c) for c in categories}
     tree = []
     for cat in categories:
         if cat.parent_id and cat.parent_id in cat_map:
             cat_map[cat.parent_id].children.append(cat_map[cat.id])
         else:
             tree.append(cat_map[cat.id])
     return tree
 
 
 @router.put("/{category_id}", response_model=CategoryResponse)
 async def update_category(category_id: str, data: CategoryUpdate,
                            current_user: User = Depends(get_current_user),
                            db: AsyncSession = Depends(get_db)):
     cat = await category_crud.update(db, category_id, **data.model_dump(exclude_none=True))
     if not cat:
         raise HTTPException(status_code=404, detail="分类不存在")
     return CategoryResponse.model_validate(cat)
 
 
 @router.delete("/{category_id}")
 async def delete_category(category_id: str, current_user: User = Depends(get_current_user),
                            db: AsyncSession = Depends(get_db)):
     success = await category_crud.delete(db, category_id)
     if not success:
         raise HTTPException(status_code=404, detail="分类不存在")
     return {"message": "分类已删除"}
 
 
 @router.post("/family/{family_id}/init-defaults")
 async def init_default_categories(family_id: str, current_user: User = Depends(get_current_user),
                                    db: AsyncSession = Depends(get_db)):
     if not await family_member_crud.is_admin(db, family_id, current_user.id):
         raise HTTPException(status_code=403, detail="需要管理员权限")
     created = []
     for cat_data in DEFAULT_CATEGORIES:
         cat = await category_crud.create(db, family_id, cat_data["name"],
                                           emoji=cat_data["emoji"], sort_order=cat_data["sort_order"])
         created.append(CategoryResponse.model_validate(cat))
     return {"message": f"已创建 {len(created)} 个默认分类", "categories": created}
