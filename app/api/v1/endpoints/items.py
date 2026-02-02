from typing import Any, List, Optional
from uuid import UUID
from fastapi import APIRouter, Depends, HTTPException, Query, status
from sqlalchemy.ext.asyncio import AsyncSession
from app.api import deps
from app.core.database import get_db
from app.schemas.item import ItemCreate, ItemResponse, ItemUpdate, PaginatedItemResponse
from app.services.item_service import ItemService
from app.models.user import User

router = APIRouter()

@router.get("/analytics/category-density")
async def get_analytics(
    db: AsyncSession = Depends(get_db),
    # current_user: User = Depends(deps.get_current_user) # Opsiyonel: Analitik herkese açık mı olsun? Genelde protected olur.
) -> Any:
    """
    Get category density analytics.
    """
    return await ItemService.get_analytics(db)

@router.get("/", response_model=PaginatedItemResponse)
async def read_items(
    db: AsyncSession = Depends(get_db),
    page: int = Query(1, ge=1),
    limit: int = Query(10, ge=1, le=100),
    category: Optional[str] = None,
    item_status: Optional[str] = Query(None, alias="status"),
    sort_by: str = Query("created_at", regex="^(created_at|name|category)$"),
    order: str = Query("desc", regex="^(asc|desc)$"),
    current_user: User = Depends(deps.get_current_user),
) -> Any:
    """
    Retrieve items.
    """
    result = await ItemService.get_multi(
        db, page=page, limit=limit, category=category, status=item_status, sort_by=sort_by, order=order
    )
    return result

@router.post("/", response_model=ItemResponse, status_code=status.HTTP_201_CREATED)
async def create_item(
    *,
    db: AsyncSession = Depends(get_db),
    item_in: ItemCreate,
    current_user: User = Depends(deps.get_current_user),
) -> Any:
    """
    Create new item.
    """
    item = await ItemService.create(db=db, item_in=item_in)
    return item

@router.get("/{id}", response_model=ItemResponse)
async def read_item(
    *,
    db: AsyncSession = Depends(get_db),
    id: UUID,
    current_user: User = Depends(deps.get_current_user),
) -> Any:
    """
    Get item by ID.
    """
    item = await ItemService.get(db=db, id=id)
    if not item:
        raise HTTPException(status_code=404, detail="Item not found")
    return item

@router.put("/{id}", response_model=ItemResponse)
async def update_item(
    *,
    db: AsyncSession = Depends(get_db),
    id: UUID,
    item_in: ItemUpdate,
    current_user: User = Depends(deps.get_current_user),
) -> Any:
    """
    Update an item.
    """
    item = await ItemService.get(db=db, id=id)
    if not item:
        raise HTTPException(status_code=404, detail="Item not found")
    item = await ItemService.update(db=db, db_item=item, item_in=item_in)
    return item

@router.delete("/{id}", response_model=ItemResponse)
async def delete_item(
    *,
    db: AsyncSession = Depends(get_db),
    id: UUID,
    current_user: User = Depends(deps.get_current_user),
) -> Any:
    """
    Delete an item (Soft delete).
    """
    item = await ItemService.get(db=db, id=id)
    if not item:
        raise HTTPException(status_code=404, detail="Item not found")
    item = await ItemService.delete(db=db, db_item=item)
    return item
