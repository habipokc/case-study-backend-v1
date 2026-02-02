from typing import Optional, List
from pydantic import BaseModel, UUID4
from datetime import datetime
from app.models.item import ItemStatus

# Shared properties
class ItemBase(BaseModel):
    name: str
    category: str
    status: Optional[ItemStatus] = ItemStatus.ACTIVE

# Properties to receive on creation
class ItemCreate(ItemBase):
    pass

# Properties to receive on update
class ItemUpdate(BaseModel):
    name: Optional[str] = None
    category: Optional[str] = None
    status: Optional[ItemStatus] = None

# Properties to return to client
class ItemResponse(ItemBase):
    id: UUID4
    created_at: datetime
    updated_at: Optional[datetime]
    deleted_at: Optional[datetime]

    class Config:
        from_attributes = True

class PaginatedItemResponse(BaseModel):
    items: List[ItemResponse]
    total: int
    page: int
    size: int
    pages: int
