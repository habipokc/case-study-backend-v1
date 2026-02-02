from typing import Any
from datetime import timedelta
from fastapi import APIRouter, Depends, HTTPException, status
from fastapi.security import OAuth2PasswordRequestForm
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select

from app.api import deps
from app.core import security
from app.core.database import get_db
from app.models.user import User
from app.services.user_service import UserService
from app.schemas.user import UserCreate, UserResponse
from app.schemas.auth import Token, RefreshTokenRequest, TokenPayload
from app.core.config import settings
from jose import jwt, JWTError
from pydantic import ValidationError

router = APIRouter()

@router.post("/refresh", response_model=Token)
async def refresh_token(
    refresh_in: RefreshTokenRequest,
    db: AsyncSession = Depends(get_db),
) -> Any:
    """
    Refresh access token using a refresh token
    """
    try:
        payload = jwt.decode(
            refresh_in.refresh_token, settings.SECRET_KEY, algorithms=[security.ALGORITHM]
        )
        token_data = TokenPayload(**payload)
    except (JWTError, ValidationError):
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Could not validate credentials",
        )
        
    # Verify it's a refresh token
    if payload.get("type") != "refresh":
         raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Invalid token type",
        )

    user = await UserService.get(db, id=token_data.sub)
    
    if not user:
        raise HTTPException(status_code=404, detail="User not found")
    if not user.is_active:
        raise HTTPException(status_code=400, detail="Inactive user")

    access_token_expires = timedelta(minutes=settings.ACCESS_TOKEN_EXPIRE_MINUTES)
    return {
        "access_token": security.create_access_token(
            user.id, expires_delta=access_token_expires
        ),
        "refresh_token": refresh_in.refresh_token, # Return same refresh token or rotate it
        "token_type": "bearer",
    }

@router.post("/login", response_model=Token)
async def login_access_token(
    db: AsyncSession = Depends(get_db),
    form_data: OAuth2PasswordRequestForm = Depends()
) -> Any:
    """
    OAuth2 compatible token login, get an access token for future requests
    """
    # Authenticate user
    user = await UserService.authenticate(
        db, email=form_data.username, password=form_data.password
    )
    
    if not user:
        raise HTTPException(status_code=400, detail="Incorrect email or password")
    if not user.is_active:
        raise HTTPException(status_code=400, detail="Inactive user")
        
    access_token_expires = timedelta(minutes=settings.ACCESS_TOKEN_EXPIRE_MINUTES)
    return {
        "access_token": security.create_access_token(
            user.id, expires_delta=access_token_expires
        ),
        "refresh_token": security.create_refresh_token(user.id),
        "token_type": "bearer",
    }

@router.post("/register", response_model=UserResponse, status_code=201)
async def register_new_user(
    *,
    db: AsyncSession = Depends(get_db),
    user_in: UserCreate,
) -> Any:
    """
    Create new user.
    """
    user = await UserService.create(db, user_in)
    if not user:
        raise HTTPException(
            status_code=400,
            detail="The user with this username already exists in the system.",
        )
    return user
