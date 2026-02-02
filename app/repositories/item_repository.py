from typing import Any, Dict, List, Optional
from datetime import datetime
from sqlalchemy import select, func
from sqlalchemy.ext.asyncio import AsyncSession
from app.models.item import Item, ItemStatus
from app.schemas.item import ItemCreate, ItemUpdate
from app.repositories.base import BaseRepository

class ItemRepository(BaseRepository[Item, ItemCreate, ItemUpdate]):
    async def get_multi_paginated(
        self, 
        db: AsyncSession, 
        page: int = 1, 
        limit: int = 10, 
        category: Optional[str] = None,
        status: Optional[str] = None,
        sort_by: str = "created_at",
        order: str = "desc"
    ) -> Dict[str, Any]:
        skip = (page - 1) * limit
        
        # Base query (Soft Delete check)
        query = select(self.model).where(self.model.deleted_at.is_(None))
        
        # Filters
        if category:
            query = query.where(self.model.category == category)
        if status:
            query = query.where(self.model.status == status)
            
        # Count total items
        count_query = select(func.count()).select_from(query.subquery())
        total_result = await db.execute(count_query)
        total = total_result.scalar() or 0
        
        # Sorting
        sort_column = getattr(self.model, sort_by, self.model.created_at)
        if order == "asc":
            query = query.order_by(sort_column.asc())
        else:
            query = query.order_by(sort_column.desc())
            
        # Pagination
        query = query.offset(skip).limit(limit)
        
        result = await db.execute(query)
        items = result.scalars().all()
        
        return {
            "items": items,
            "total": total,
            "page": page,
            "size": limit,
            "pages": (total + limit - 1) // limit if limit > 0 else 0
        }

    # Override delete for Soft Delete
    async def delete(self, db: AsyncSession, *, db_obj: Item) -> Item:
        db_obj.deleted_at = datetime.utcnow()
        db_obj.status = ItemStatus.INACTIVE
        db.add(db_obj)
        await db.commit()
        await db.refresh(db_obj)
        return db_obj

    async def get_analytics(self, db: AsyncSession) -> Dict[str, Any]:
        """
        Calculates category density statistics with Caching.
        """
        # 1. Check Cache
        import json
        from app.core.redis import redis_client
        
        cache_key = "analytics:category_density"
        cached_data = await redis_client.get_value(cache_key)
        if cached_data:
            return json.loads(cached_data)

        # 2. Calculate if cache miss
        # Get total non-deleted items count
        total_query = select(func.count(Item.id)).where(Item.deleted_at.is_(None))
        total_result = await db.execute(total_query)
        total_items = total_result.scalar() or 0
        
        result_data = {}

        if total_items == 0:
            result_data = {
                "success": True,
                "data": {
                    "total_items": 0,
                    "categories": []
                }
            }
        else:
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
                
            result_data = {
                "success": True,
                "data": {
                    "total_items": total_items,
                    "categories": categories_data
                }
            }
            
        # 3. Set Cache (60 seconds)
        await redis_client.set_value(cache_key, json.dumps(result_data), expire=60)
        
        return result_data

item_repository = ItemRepository(Item)
