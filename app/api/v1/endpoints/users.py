from typing import Any
from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select

from app.api import deps
from app.core.database import get_db
from app.models.user import User
from app.services.user_service import UserService
from app.schemas.user import UserResponse, UserUpdate

router = APIRouter()

@router.get("/profile", response_model=UserResponse)
async def read_user_profile(
    current_user: User = Depends(deps.get_current_user),
) -> Any:
    """
    Get current user profile.
    """
    return current_user

@router.put("/profile", response_model=UserResponse)
async def update_user_profile(
    *,
    db: AsyncSession = Depends(get_db),
    user_in: UserUpdate,
    current_user: User = Depends(deps.get_current_user),
) -> Any:
    """
    Update current user profile.
    """
    user = await UserService.update(db, db_user=current_user, user_in=user_in)
    return user
