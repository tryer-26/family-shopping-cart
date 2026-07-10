from sqlalchemy import select, and_
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.orm import joinedload

from app.models.family import Family, FamilyMember, FamilyRole
from app.models.user import User
from app.utils.security import generate_uuid


class FamilyCRUD:
    async def create(self, db: AsyncSession, name: str, created_by: str, description: str | None = None, emoji: str | None = None) -> Family:
        family = Family(
            name=name, description=description, emoji=emoji, created_by=created_by
        )
        db.add(family)
        await db.flush()
        await db.refresh(family)
        # Add creator as admin
        member = FamilyMember(family_id=family.id, user_id=created_by, role=FamilyRole.ADMIN)
        db.add(member)
        await db.flush()
        return family

    async def get_by_id(self, db: AsyncSession, family_id: str) -> Family | None:
        result = await db.execute(
            select(Family).options(joinedload(Family.members)).where(Family.id == family_id)
        )
        return result.unique().scalar_one_or_none()

    async def get_user_families(self, db: AsyncSession, user_id: str) -> list[Family]:
        result = await db.execute(
            select(Family).join(FamilyMember).where(
                and_(FamilyMember.user_id == user_id, FamilyMember.family_id == Family.id)
            )
        )
        return list(result.scalars().all())

    async def update(self, db: AsyncSession, family_id: str, **kwargs) -> Family | None:
        family = await self.get_by_id(db, family_id)
        if not family:
            return None
        for key, value in kwargs.items():
            if value is not None and hasattr(family, key):
                setattr(family, key, value)
        await db.flush()
        await db.refresh(family)
        return family

    async def delete(self, db: AsyncSession, family_id: str) -> bool:
        family = await self.get_by_id(db, family_id)
        if not family:
            return False
        await db.delete(family)
        await db.flush()
        return True


class FamilyMemberCRUD:
    async def get_members(self, db: AsyncSession, family_id: str) -> list[dict]:
        result = await db.execute(
            select(FamilyMember, User.username, User.email, User.avatar)
            .join(User, FamilyMember.user_id == User.id)
            .where(FamilyMember.family_id == family_id)
        )
        members = []
        for row in result.all():
            fm, username, email, avatar = row
            members.append({
                "id": fm.id,
                "user_id": fm.user_id,
                "username": username,
                "email": email,
                "avatar": avatar,
                "role": fm.role,
                "joined_at": fm.joined_at,
            })
        return members

    async def add_member(self, db: AsyncSession, family_id: str, user_id: str, role: FamilyRole = FamilyRole.MEMBER) -> FamilyMember | None:
        existing = await db.execute(
            select(FamilyMember).where(
                and_(FamilyMember.family_id == family_id, FamilyMember.user_id == user_id)
            )
        )
        if existing.scalar_one_or_none():
            return None
        member = FamilyMember(family_id=family_id, user_id=user_id, role=role)
        db.add(member)
        await db.flush()
        await db.refresh(member)
        return member

    async def update_role(self, db: AsyncSession, family_id: str, user_id: str, role: FamilyRole) -> bool:
        result = await db.execute(
            select(FamilyMember).where(
                and_(FamilyMember.family_id == family_id, FamilyMember.user_id == user_id)
            )
        )
        member = result.scalar_one_or_none()
        if not member:
            return False
        member.role = role
        await db.flush()
        return True

    async def remove_member(self, db: AsyncSession, family_id: str, user_id: str) -> bool:
        result = await db.execute(
            select(FamilyMember).where(
                and_(FamilyMember.family_id == family_id, FamilyMember.user_id == user_id)
            )
        )
        member = result.scalar_one_or_none()
        if not member:
            return False
        await db.delete(member)
        await db.flush()
        return True

    async def is_member(self, db: AsyncSession, family_id: str, user_id: str) -> bool:
        result = await db.execute(
            select(FamilyMember).where(
                and_(FamilyMember.family_id == family_id, FamilyMember.user_id == user_id)
            )
        )
        return result.scalar_one_or_none() is not None

    async def is_admin(self, db: AsyncSession, family_id: str, user_id: str) -> bool:
        result = await db.execute(
            select(FamilyMember).where(
                and_(
                    FamilyMember.family_id == family_id,
                    FamilyMember.user_id == user_id,
                    FamilyMember.role == FamilyRole.ADMIN,
                )
            )
        )
        return result.scalar_one_or_none() is not None


family_crud = FamilyCRUD()
family_member_crud = FamilyMemberCRUD()
