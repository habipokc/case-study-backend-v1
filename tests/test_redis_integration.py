import pytest
import asyncio
from httpx import AsyncClient
from app.core.config import settings

# Helper to register and login user is reused from previous flows or we create fresh one here
# We assume the DB is running (via Docker) and Uvicorn is running application code.
# Since we are running integrations tests against the 'app' instance created in conftest, 
# we need to make sure Redis is also reachable.

@pytest.mark.asyncio
async def test_redis_blacklist_flow(ac: AsyncClient):
    # 1. Register & Login
    email = "redis_user@example.com"
    password = "redispassword"
    
    # Try register (ignore if exists)
    await ac.post("/api/v1/auth/register", json={
        "email": email, "password": password, "first_name": "Redis", "last_name": "Test"
    })
    
    login_resp = await ac.post("/api/v1/auth/login", data={"username": email, "password": password})
    assert login_resp.status_code == 200
    token = login_resp.json()["access_token"]
    headers = {"Authorization": f"Bearer {token}"}
    
    # 2. Access Protected Endpoint
    resp = await ac.get("/api/v1/users/profile", headers=headers)
    assert resp.status_code == 200
    assert resp.json()["email"] == email
    
    # 3. Logout
    logout_resp = await ac.post("/api/v1/auth/logout", headers=headers)
    assert logout_resp.status_code == 200
    
    # 4. Access Protected Endpoint Again (Should Fail)
    resp_after_logout = await ac.get("/api/v1/users/profile", headers=headers)
    assert resp_after_logout.status_code == 401
    # Check 'message' key as configured in http_exception_handler
    assert resp_after_logout.json()["message"] == "Token has been revoked"
