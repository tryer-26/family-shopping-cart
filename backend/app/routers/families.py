 from fastapi import APIRouter, Depends, HTTPException, status
 from sqlalchemy.ext.asyncio import AsyncSession
 
 from app.database import get_db
 from app.dependencies import get_current_user
 from app.models.user import User
 from app.schemas.family import (
     FamilyCreate, FamilyUpdate, FamilyResponse, FamilyMemberResponse,
     FamilyMemberAdd, FamilyMemberUpdate, FamilyWithMembers,
 )
 from app.crud.family import family_crud, family_member_crud
 from app.models.family import FamilyRole
 
 router = APIRouter(prefix="/families", tags=["家庭管理"])
 
 
 @router.post("", response_model=FamilyResponse, status_code=status.HTTP_201_CREATED)
 async def create_family(data: FamilyCreate, current_user: User = Depends(get_current_user),
                          db: AsyncSession = Depends(get_db)):
     family = await family_crud.create(db, data.name, current_user.id, data.description, data.emoji)
     return FamilyResponse.model_validate(family)
 
 
 @router.get("", response_model=list[FamilyResponse])
 async def list_families(current_user: User = Depends(get_current_user),
                          db: AsyncSession = Depends(get_db)):
     families = await family_crud.get_user_families(db, current_user.id)
     return [FamilyResponse.model_validate(f) for f in families]
 
 
 @router.get("/{family_id}", response_model=FamilyWithMembers)
 async def get_family(family_id: str, current_user: User = Depends(get_current_user),
                       db: AsyncSession = Depends(get_db)):
     if not await family_member_crud.is_member(db, family_id, current_user.id):
         raise HTTPException(status_code=403, detail="不是家庭成员")
     family = await family_crud.get_by_id(db, family_id)
     if not family:
         raise HTTPException(status_code=404, detail="家庭不存在")
     members = await family_member_crud.get_members(db, family_id)
     return FamilyWithMembers(
         family=FamilyResponse.model_validate(family),
         members=[FamilyMemberResponse(**m) for m in members],
     )
 
 
 @router.put("/{family_id}", response_model=FamilyResponse)
 async def update_family(family_id: str, data: FamilyUpdate,
                          current_user: User = Depends(get_current_user),
                          db: AsyncSession = Depends(get_db)):
     if not await family_member_crud.is_admin(db, family_id, current_user.id):
         raise HTTPException(status_code=403, detail="需要管理员权限")
     family = await family_crud.update(db, family_id, **data.model_dump(exclude_none=True))
     if not family:
         raise HTTPException(status_code=404, detail="家庭不存在")
     return FamilyResponse.model_validate(family)
 
 
 @router.delete("/{family_id}")
 async def delete_family(family_id: str, current_user: User = Depends(get_current_user),
                          db: AsyncSession = Depends(get_db)):
     if not await family_member_crud.is_admin(db, family_id, current_user.id):
         raise HTTPException(status_code=403, detail="需要管理员权限")
     success = await family_crud.delete(db, family_id)
     if not success:
         raise HTTPException(status_code=404, detail="家庭不存在")
     return {"message": "家庭已删除"}
 
 
 @router.post("/{family_id}/members", response_model=FamilyMemberResponse, status_code=status.HTTP_201_CREATED)
 async def add_member(family_id: str, data: FamilyMemberAdd,
                       current_user: User = Depends(get_current_user),
                       db: AsyncSession = Depends(get_db)):
     if not await family_member_crud.is_admin(db, family_id, current_user.id):
         raise HTTPException(status_code=403, detail="需要管理员权限")
     member = await family_member_crud.add_member(db, family_id, data.user_id, data.role)
     if not member:
         raise HTTPException(status_code=400, detail="成员已存在")
     members = await family_member_crud.get_members(db, family_id)
     for m in members:
         if m["user_id"] == data.user_id:
             return FamilyMemberResponse(**m)
     raise HTTPException(status_code=500, detail="添加失败")
 
 
 @router.put("/{family_id}/members/{user_id}/role")
 async def update_member_role(family_id: str, user_id: str, data: FamilyMemberUpdate,
                               current_user: User = Depends(get_current_user),
                               db: AsyncSession = Depends(get_db)):
     if not await family_member_crud.is_admin(db, family_id, current_user.id):
         raise HTTPException(status_code=403, detail="需要管理员权限")
     success = await family_member_crud.update_role(db, family_id, user_id, data.role)
     if not success:
         raise HTTPException(status_code=404, detail="成员不存在")
     return {"message": "角色已更新"}
 
 
 @router.delete("/{family_id}/members/{user_id}")
 async def remove_member(family_id: str, user_id: str,
                          current_user: User = Depends(get_current_user),
                          db: AsyncSession = Depends(get_db)):
     if not await family_member_crud.is_admin(db, family_id, current_user.id):
         raise HTTPException(status_code=403, detail="需要管理员权限")
     if current_user.id == user_id:
         raise HTTPException(status_code=400, detail="不能移除自己")
     success = await family_member_crud.remove_member(db, family_id, user_id)
     if not success:
         raise HTTPException(status_code=404, detail="成员不存在")
     return {"message": "成员已移除"}
 
 
 @router.get("/{family_id}/members", response_model=list[FamilyMemberResponse])
 async def list_members(family_id: str, current_user: User = Depends(get_current_user),
                         db: AsyncSession = Depends(get_db)):
     if not await family_member_crud.is_member(db, family_id, current_user.id):
         raise HTTPException(status_code=403, detail="不是家庭成员")
     members = await family_member_crud.get_members(db, family_id)
     return [FamilyMemberResponse(**m) for m in members]
