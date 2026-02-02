from typing import Optional
from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession
from app.models.user import User
from app.schemas.user import UserCreate, UserUpdate
from app.repositories.base import BaseRepository

class UserRepository(BaseRepository[User, UserCreate, UserUpdate]):
    async def get_by_email(self, db: AsyncSession, *, email: str) -> Optional[User]:
        query = select(self.model).where(self.model.email == email)
        result = await db.execute(query)
        return result.scalars().first()

user_repository = UserRepository(User)
