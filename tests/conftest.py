import asyncio
from typing import AsyncGenerator

import pytest
from httpx import ASGITransport, AsyncClient
from sqlalchemy.ext.asyncio import AsyncSession

from app.core.database import engine, get_db
from app.main import app


# -------------------------------------------------
# Event loop (pytest-asyncio uyumlu)
# -------------------------------------------------
@pytest.fixture(scope="session")
def event_loop():
    loop = asyncio.new_event_loop()
    yield loop
    loop.close()


# -------------------------------------------------
# DB session – HER TEST İÇİN TRANSACTION + ROLLBACK
# -------------------------------------------------
@pytest.fixture
async def db_session():
    async with engine.connect() as connection:
        transaction = await connection.begin()
        session = AsyncSession(bind=connection)

        try:
            yield session
        finally:
            await session.close()
            await transaction.rollback()


# -------------------------------------------------
# get_db dependency override (KRİTİK NOKTA)
# -------------------------------------------------
@pytest.fixture(autouse=True)
async def override_get_db(db_session):
    async def _get_db_override():
        yield db_session

    app.dependency_overrides[get_db] = _get_db_override
    yield
    app.dependency_overrides.clear()


# -------------------------------------------------
# Redis setup (seninki aynen korunuyor)
# -------------------------------------------------
@pytest.fixture(autouse=True)
async def setup_redis():
    from app.core.redis import redis_client

    await redis_client.connect()
    yield
    await redis_client.close()


# -------------------------------------------------
# HTTP client
# -------------------------------------------------
@pytest.fixture
async def ac() -> AsyncGenerator[AsyncClient, None]:
    transport = ASGITransport(app=app)
    async with AsyncClient(transport=transport, base_url="http://test") as client:
        yield client
