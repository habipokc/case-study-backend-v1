from fastapi import APIRouter
from app.api.v1.endpoints import auth, users, items

api_router = APIRouter()
# Auth endpoints under /users to match case study: /api/users/register, /api/users/login
api_router.include_router(auth.router, prefix="/users", tags=["auth"])
api_router.include_router(users.router, prefix="/users", tags=["users"])
api_router.include_router(items.router, prefix="/items", tags=["items"])
