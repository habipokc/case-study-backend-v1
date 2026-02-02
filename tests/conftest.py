"""
Test Configuration with Database Isolation
- Uses separate test database via TEST_DATABASE_URL
- Transaction rollback per test
- Redis flush between tests
"""
import asyncio
import uuid
from typing import AsyncGenerator

import pytest
from httpx import ASGITransport, AsyncClient
from sqlalchemy.ext.asyncio import AsyncSession, create_async_engine
from sqlalchemy.pool import NullPool

from app.core.config import settings
from app.core.database import Base, get_db
from app.main import app


# -------------------------------------------------
# Test Database Configuration
# -------------------------------------------------
TEST_DATABASE_URL = settings.TEST_DATABASE_URL or settings.DATABASE_URL

# Create test engine
test_engine = create_async_engine(
    TEST_DATABASE_URL,
    poolclass=NullPool,
    echo=False
)


# -------------------------------------------------
# Event loop (pytest-asyncio compatible)
# -------------------------------------------------
@pytest.fixture(scope="session")
def event_loop():
    """Create event loop for test session."""
    loop = asyncio.new_event_loop()
    yield loop
    loop.close()


# -------------------------------------------------
# DB Session with Transaction Rollback
# -------------------------------------------------
@pytest.fixture
async def db_session():
    """
    Provide a database session with transaction rollback.
    """
    # Create tables if they don't exist
    async with test_engine.begin() as conn:
        await conn.run_sync(Base.metadata.create_all)
    
    async with test_engine.connect() as connection:
        transaction = await connection.begin()
        session = AsyncSession(bind=connection, expire_on_commit=False)
        
        try:
            yield session
        finally:
            await session.close()
            await transaction.rollback()


# -------------------------------------------------
# Override get_db dependency
# -------------------------------------------------
@pytest.fixture(autouse=True)
async def override_get_db(db_session):
    """Override FastAPI's get_db dependency to use test session."""
    async def _get_db_override():
        yield db_session
    
    app.dependency_overrides[get_db] = _get_db_override
    yield
    app.dependency_overrides.clear()


# -------------------------------------------------
# Redis Setup & Cleanup
# -------------------------------------------------
@pytest.fixture(autouse=True)
async def setup_redis():
    """Connect to Redis and flush before each test."""
    from app.core.redis import redis_client
    
    await redis_client.connect()
    
    # Flush Redis for clean state
    if redis_client.redis_client:
        await redis_client.redis_client.flushdb()
    
    yield
    
    await redis_client.close()


# -------------------------------------------------
# HTTP Test Client
# -------------------------------------------------
@pytest.fixture
async def ac() -> AsyncGenerator[AsyncClient, None]:
    """Provide async HTTP client for API testing."""
    transport = ASGITransport(app=app)
    async with AsyncClient(transport=transport, base_url="http://test") as client:
        yield client


# -------------------------------------------------
# Helper: Generate unique test email
# -------------------------------------------------
@pytest.fixture
def unique_email():
    """Generate a unique email for each test."""
    return f"test_{uuid.uuid4()}@example.com"
