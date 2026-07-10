 from fastapi import APIRouter, Depends
 
 router = APIRouter(prefix="/users", tags=["用户管理"])
 
 # User management is primarily handled via /auth/me
 # This router can be extended for admin user management in the future
 
 @router.get("/health")
 async def health():
     return {"status": "ok", "service": "users"}
