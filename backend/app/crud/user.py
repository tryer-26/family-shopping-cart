from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from app.models.user import User
from app.utils.security import hash_password, verify_password


class UserCRUD:
   async def create(self, db: AsyncSession, username: str, email: str, password: str, phone: str | None = None) -> User:
       user = User(
           username=username,
           email=email,
           password_hash=hash_password(password),
           phone=phone,
       )
       db.add(user)
       await db.flush()
       await db.refresh(user)
       return user

   async def get_by_id(self, db: AsyncSession, user_id: str) -> User | None:
       result = await db.execute(select(User).where(User.id == user_id))
       return result.scalar_one_or_none()

   async def get_by_username(self, db: AsyncSession, username: str) -> User | None:
       result = await db.execute(select(User).where(User.username == username))
       return result.scalar_one_or_none()

   async def get_by_email(self, db: AsyncSession, email: str) -> User | None:
       result = await db.execute(select(User).where(User.email == email))
       return result.scalar_one_or_none()

   async def authenticate(self, db: AsyncSession, username: str, password: str) -> User | None:
       user = await self.get_by_username(db, username)
       if not user:
           user = await self.get_by_email(db, username)
       if user and verify_password(password, user.password_hash):
           return user
       return None

   async def update(self, db: AsyncSession, user_id: str, **kwargs) -> User | None:
       user = await self.get_by_id(db, user_id)
       if not user:
           return None
       for key, value in kwargs.items():
           if value is not None and hasattr(user, key):
               if key == "password":
                   setattr(user, "password_hash", hash_password(value))
               else:
                   setattr(user, key, value)
       await db.flush()
       await db.refresh(user)
       return user

   async def change_password(self, db: AsyncSession, user_id: str, old_password: str, new_password: str) -> bool:
       user = await self.get_by_id(db, user_id)
       if not user or not verify_password(old_password, user.password_hash):
           return False
       user.password_hash = hash_password(new_password)
       await db.flush()
       return True


user_crud = UserCRUD()
