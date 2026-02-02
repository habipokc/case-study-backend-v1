import pytest
from typing import AsyncGenerator
from httpx import AsyncClient
from sqlalchemy.ext.asyncio import AsyncSession, create_async_engine
from sqlalchemy.orm import sessionmaker
from app.main import app
from app.core.database import Base, get_db
from app.core.config import settings

# Use an in-memory SQLite database for testing or a separate test DB
# For this case study, we'll try to stick to the same DB or ideally a test DB
# To keep it simple and robust without spinning up another container, 
# we will use the existing DB but transaction rollbacks or a separate test DB if possible.
# Ideally: DATABASE_URL_TEST = "postgresql+asyncpg://postgres:postgres@localhost:5432/test_db"
# But creating DBs dynamically might be complex. 
# Let's use the Dependency Override pattern with a rollback transaction for isolation if possible.

@pytest.fixture
async def ac() -> AsyncGenerator[AsyncClient, None]:
    async with AsyncClient(app=app, base_url="http://test") as c:
        yield c
