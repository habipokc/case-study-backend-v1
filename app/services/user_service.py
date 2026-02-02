from typing import Optional
from uuid import UUID
from sqlalchemy.ext.asyncio import AsyncSession
from app.models.user import User
from app.schemas.user import UserCreate, UserUpdate
from app.repositories.user_repository import user_repository
from app.core.security import get_password_hash, verify_password

class UserService:
    @staticmethod
    async def get(db: AsyncSession, id: UUID) -> Optional[User]:
        return await user_repository.get(db, id)

    @staticmethod
    async def get_by_email(db: AsyncSession, email: str) -> Optional[User]:
        return await user_repository.get_by_email(db, email=email)

    @staticmethod
    async def create(db: AsyncSession, user_in: UserCreate) -> User:
        # Check if user exists
        existing_user = await user_repository.get_by_email(db, email=user_in.email)
        if existing_user:
            return None # Or raise exception, but service usually returns result or None/False

        # Create new user with hashed password
        # We need to manually construct the User object or modify UserCreate to store hash
        # But BaseRepository takes CreateSchemaType. 
        # Ideally we pass a dict to repository or modify the schema object.
        # Let's create the db object manually here or override repository create?
        # A cleaner way: The Repository 'create' method takes a Schema. 
        # But we need to hash the password. The schema has 'password' (plain). 
        # The model has 'password_hash'. 
        
        # Method: We can prepare the dict manually and use the model constructor in repository,
        # OR we can just do it here since BaseRepository.create uses model(**obj_in_data).
        
        hashed_password = get_password_hash(user_in.password)
        
        db_user = User(
            email=user_in.email,
            password_hash=hashed_password,
            first_name=user_in.first_name,
            last_name=user_in.last_name,
            is_active=True
        )
        db.add(db_user)
        await db.commit()
        await db.refresh(db_user)
        return db_user

    @staticmethod
    async def authenticate(db: AsyncSession, email: str, password: str) -> Optional[User]:
        user = await user_repository.get_by_email(db, email=email)
        if not user:
            return None
        if not verify_password(password, user.password_hash):
            return None
        return user

    @staticmethod
    async def update(db: AsyncSession, db_user: User, user_in: UserUpdate) -> User:
        return await user_repository.update(db, db_obj=db_user, obj_in=user_in)
