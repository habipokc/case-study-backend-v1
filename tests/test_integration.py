"""
Integration Tests for Case Study Backend
Tests complete user flows and item CRUD operations with proper isolation.
"""
import uuid

import pytest
from httpx import AsyncClient


@pytest.mark.asyncio
async def test_user_flow_and_items(ac: AsyncClient, unique_email: str):
    """
    Test complete user registration, login, and item CRUD flow.
    """
    password = "securepassword123"
    
    # 1. Register
    register_data = {
        "email": unique_email,
        "password": password,
        "first_name": "Test",
        "last_name": "User"
    }
    response = await ac.post("/api/v1/users/register", json=register_data)
    assert response.status_code == 201
    user_data = response.json()
    assert "id" in user_data
    assert user_data["email"] == unique_email

    # 2. Login
    response = await ac.post("/api/v1/users/login", data={
        "username": unique_email,
        "password": password
    })
    assert response.status_code == 200
    tokens = response.json()
    assert "access_token" in tokens
    assert "refresh_token" in tokens
    access_token = tokens["access_token"]
    headers = {"Authorization": f"Bearer {access_token}"}

    # 3. Get Profile
    response = await ac.get("/api/v1/users/profile", headers=headers)
    assert response.status_code == 200
    assert response.json()["email"] == unique_email

    # 4. Update Profile
    response = await ac.put("/api/v1/users/profile", headers=headers, json={
        "first_name": "Updated",
        "last_name": "Name"
    })
    assert response.status_code == 200
    assert response.json()["first_name"] == "Updated"

    # 5. Create Item
    item_data = {
        "name": "Integration Test Item",
        "category": "Testing"
    }
    response = await ac.post("/api/v1/items/", json=item_data, headers=headers)
    assert response.status_code == 201
    item = response.json()
    item_id = item["id"]
    assert item["name"] == item_data["name"]
    assert item["status"] == "active"

    # 6. Get Item
    response = await ac.get(f"/api/v1/items/{item_id}", headers=headers)
    assert response.status_code == 200
    assert response.json()["id"] == item_id

    # 7. Update Item
    response = await ac.put(f"/api/v1/items/{item_id}", json={"name": "Updated Name"}, headers=headers)
    assert response.status_code == 200
    assert response.json()["name"] == "Updated Name"

    # 8. Analytics Check
    response = await ac.get("/api/v1/items/analytics/category-density", headers=headers)
    assert response.status_code == 200
    analytics = response.json()
    assert analytics["success"] is True
    assert "total_items" in analytics["data"]

    # 9. Delete Item (Soft Delete)
    response = await ac.delete(f"/api/v1/items/{item_id}", headers=headers)
    assert response.status_code == 200
    deleted_item = response.json()
    assert deleted_item["status"] == "inactive"
    assert deleted_item["deleted_at"] is not None

    # 10. Verify Soft Delete (item not in list)
    response = await ac.get("/api/v1/items/", headers=headers)
    assert response.status_code == 200
    items = response.json().get('items', [])
    assert not any(i["id"] == item_id for i in items)


@pytest.mark.asyncio
async def test_validation_errors(ac: AsyncClient, unique_email: str):
    """
    Test validation error handling.
    """
    password = "securepassword123"
    
    # Register and login
    await ac.post("/api/v1/users/register", json={
        "email": unique_email, 
        "password": password, 
        "first_name": "Val", 
        "last_name": "User"
    })
    login_resp = await ac.post("/api/v1/users/login", data={
        "username": unique_email, 
        "password": password
    })
    token = login_resp.json()["access_token"]
    headers = {"Authorization": f"Bearer {token}"}
    
    # 1. Invalid UUID
    resp = await ac.get("/api/v1/items/not-a-uuid", headers=headers)
    assert resp.status_code == 422  # Validation Error
    
    # 2. Non-existent Item
    random_id = uuid.uuid4()
    resp = await ac.get(f"/api/v1/items/{random_id}", headers=headers)
    assert resp.status_code == 404


@pytest.mark.asyncio
async def test_analytics_with_multiple_items(ac: AsyncClient, unique_email: str):
    """
    Test analytics calculation with multiple items.
    """
    password = "analyticstest123"
    
    # Register and login
    await ac.post("/api/v1/users/register", json={
        "email": unique_email,
        "password": password,
        "first_name": "Analytics",
        "last_name": "Test"
    })
    login_resp = await ac.post("/api/v1/users/login", data={
        "username": unique_email,
        "password": password
    })
    token = login_resp.json()["access_token"]
    headers = {"Authorization": f"Bearer {token}"}
    
    # Create items in different categories
    for i in range(3):
        await ac.post("/api/v1/items/", headers=headers, json={
            "name": f"Phone {i}",
            "category": "Electronics"
        })
    
    await ac.post("/api/v1/items/", headers=headers, json={
        "name": "Book",
        "category": "Books"
    })
    
    # Check analytics
    resp = await ac.get("/api/v1/items/analytics/category-density", headers=headers)
    assert resp.status_code == 200
    
    data = resp.json()["data"]
    assert data["total_items"] >= 4
    
    categories = {c["category"]: c for c in data["categories"]}
    assert "Electronics" in categories
    assert "Books" in categories
    assert categories["Electronics"]["count"] >= 3
    assert categories["Books"]["count"] >= 1


@pytest.mark.asyncio
async def test_duplicate_email_registration(ac: AsyncClient, unique_email: str):
    """
    Test that duplicate email registration fails.
    """
    password = "testpass123"
    
    # First registration should succeed
    resp1 = await ac.post("/api/v1/users/register", json={
        "email": unique_email,
        "password": password,
        "first_name": "First",
        "last_name": "User"
    })
    assert resp1.status_code == 201
    
    # Second registration with same email should fail
    resp2 = await ac.post("/api/v1/users/register", json={
        "email": unique_email,
        "password": password,
        "first_name": "Second",
        "last_name": "User"
    })
    assert resp2.status_code == 400


@pytest.mark.asyncio
async def test_unauthorized_access(ac: AsyncClient):
    """
    Test that protected endpoints return 401 without token.
    """
    # Try to access protected endpoint without auth
    resp = await ac.get("/api/v1/users/profile")
    assert resp.status_code in [401, 403]
    
    resp = await ac.get("/api/v1/items/")
    assert resp.status_code in [401, 403]
