"""
Redis Integration Tests
Tests token blacklist functionality with proper isolation.
"""
import pytest
from httpx import AsyncClient


@pytest.mark.asyncio
async def test_redis_blacklist_flow(ac: AsyncClient, unique_email: str):
    """
    Test the complete logout/blacklist flow:
    1. Register & Login
    2. Access protected endpoint
    3. Logout (token gets blacklisted)
    4. Verify blacklisted token is rejected
    """
    password = "redispassword123"
    
    # 1. Register
    register_resp = await ac.post("/api/v1/users/register", json={
        "email": unique_email, 
        "password": password, 
        "first_name": "Redis", 
        "last_name": "Test"
    })
    assert register_resp.status_code == 201
    
    # 2. Login
    login_resp = await ac.post("/api/v1/users/login", data={
        "username": unique_email, 
        "password": password
    })
    assert login_resp.status_code == 200
    token = login_resp.json()["access_token"]
    headers = {"Authorization": f"Bearer {token}"}
    
    # 3. Access Protected Endpoint (should work)
    resp = await ac.get("/api/v1/users/profile", headers=headers)
    assert resp.status_code == 200
    assert resp.json()["email"] == unique_email
    
    # 4. Logout
    logout_resp = await ac.post("/api/v1/users/logout", headers=headers)
    assert logout_resp.status_code == 200
    assert logout_resp.json()["message"] == "Successfully logged out"
    
    # 5. Access Protected Endpoint Again (should fail - token blacklisted)
    resp_after_logout = await ac.get("/api/v1/users/profile", headers=headers)
    assert resp_after_logout.status_code == 401
    assert resp_after_logout.json()["message"] == "Token has been revoked"


@pytest.mark.asyncio
async def test_refresh_token_flow(ac: AsyncClient, unique_email: str):
    """
    Test refresh token functionality.
    """
    password = "refreshtest123"
    
    # Register & Login
    await ac.post("/api/v1/users/register", json={
        "email": unique_email,
        "password": password,
        "first_name": "Refresh",
        "last_name": "Test"
    })
    
    login_resp = await ac.post("/api/v1/users/login", data={
        "username": unique_email,
        "password": password
    })
    assert login_resp.status_code == 200
    tokens = login_resp.json()
    
    assert "access_token" in tokens
    assert "refresh_token" in tokens
    
    # Use refresh token to get new access token
    refresh_resp = await ac.post("/api/v1/users/refresh", json={
        "refresh_token": tokens["refresh_token"]
    })
    assert refresh_resp.status_code == 200
    
    new_tokens = refresh_resp.json()
    assert "access_token" in new_tokens
    assert "refresh_token" in new_tokens
    # Note: Token might be identical if generated in same second (same exp timestamp)
