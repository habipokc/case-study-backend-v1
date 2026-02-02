from typing import List, Optional, Dict, Any
from uuid import UUID
from datetime import datetime
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select, func, desc
from app.models.item import Item, ItemStatus
from app.schemas.item import ItemCreate, ItemUpdate

class ItemService:
    @staticmethod
    async def get_multi(
        db: AsyncSession, 
        skip: int = 0, 
        limit: int = 100, 
        category: Optional[str] = None,
        status: Optional[str] = None
    ) -> List[Item]:
        query = select(Item).where(Item.deleted_at.is_(None))
        
        if category:
            query = query.where(Item.category == category)
        if status:
            query = query.where(Item.status == status)
            
        query = query.offset(skip).limit(limit).order_by(desc(Item.created_at))
        result = await db.execute(query)
        return result.scalars().all()

    @staticmethod
    async def get(db: AsyncSession, id: UUID) -> Optional[Item]:
        query = select(Item).where(Item.id == id, Item.deleted_at.is_(None))
        result = await db.execute(query)
        return result.scalars().first()

    @staticmethod
    async def create(db: AsyncSession, item_in: ItemCreate) -> Item:
        db_item = Item(
            name=item_in.name,
            category=item_in.category,
            status=item_in.status
        )
        db.add(db_item)
        await db.commit()
        await db.refresh(db_item)
        return db_item

    @staticmethod
    async def update(db: AsyncSession, db_item: Item, item_in: ItemUpdate) -> Item:
        update_data = item_in.model_dump(exclude_unset=True)
        for field, value in update_data.items():
            setattr(db_item, field, value)
            
        await db.commit()
        await db.refresh(db_item)
        return db_item

    @staticmethod
    async def delete(db: AsyncSession, db_item: Item) -> Item:
        # Soft delete
        db_item.deleted_at = datetime.utcnow()
        db_item.status = ItemStatus.INACTIVE
        await db.commit()
        await db.refresh(db_item)
        return db_item

    @staticmethod
    async def get_analytics(db: AsyncSession) -> Dict[str, Any]:
        """
        Calculates category density statistics.
        """
        # Get total non-deleted items count
        total_query = select(func.count(Item.id)).where(Item.deleted_at.is_(None))
        total_result = await db.execute(total_query)
        total_items = total_result.scalar() or 0
        
        if total_items == 0:
            return {
                "success": True,
                "data": {
                    "total_items": 0,
                    "categories": []
                }
            }

        # Get count per category
        cat_query = (
            select(Item.category, func.count(Item.id))
            .where(Item.deleted_at.is_(None))
            .group_by(Item.category)
        )
        cat_result = await db.execute(cat_query)
        
        categories_data = []
        for category, count in cat_result:
            categories_data.append({
                "category": category,
                "count": count,
                "percentage": round((count / total_items) * 100, 1)
            })
            
        return {
            "success": True,
            "data": {
                "total_items": total_items,
                "categories": categories_data
            }
        }
