from typing import List, Optional, Dict, Any
from uuid import UUID
from sqlalchemy.ext.asyncio import AsyncSession
from app.models.item import Item
from app.schemas.item import ItemCreate, ItemUpdate
from app.repositories.item_repository import item_repository

class ItemService:
    @staticmethod
    async def get_multi(
        db: AsyncSession, 
        page: int = 1, 
        limit: int = 10, 
        category: Optional[str] = None,
        status: Optional[str] = None,
        sort_by: str = "created_at",
        order: str = "desc"
    ) -> Dict[str, Any]:
        return await item_repository.get_multi_paginated(
            db, page=page, limit=limit, category=category, status=status, sort_by=sort_by, order=order
        )

    @staticmethod
    async def get(db: AsyncSession, id: UUID) -> Optional[Item]:
        item = await item_repository.get(db, id)
        if item and item.deleted_at:
            return None
        return item

    @staticmethod
    async def create(db: AsyncSession, item_in: ItemCreate) -> Item:
        return await item_repository.create(db, obj_in=item_in)

    @staticmethod
    async def update(db: AsyncSession, db_item: Item, item_in: ItemUpdate) -> Item:
        return await item_repository.update(db, db_obj=db_item, obj_in=item_in)

    @staticmethod
    async def delete(db: AsyncSession, db_item: Item) -> Item:
        return await item_repository.delete(db, db_obj=db_item)

    @staticmethod
    async def get_analytics(db: AsyncSession) -> Dict[str, Any]:
        return await item_repository.get_analytics(db)
