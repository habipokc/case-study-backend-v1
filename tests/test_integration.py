import pytest
from httpx import AsyncClient
import uuid

# Helper to generate unique emails
def random_email():
    return f"testuser_{uuid.uuid4()}@example.com"

@pytest.mark.asyncio
async def test_user_flow_and_items(ac: AsyncClient):
    # 1. Register
    email = random_email()
    password = "securepassword123"
    register_data = {
        "email": email,
        "password": password,
        "first_name": "Test",
        "last_name": "User"
    }
    response = await ac.post("/api/v1/users/register", json=register_data)
    assert response.status_code == 201
    user_id = response.json()["id"]

    # 2. Login
    login_data = {
        "username": email,
        "password": password
    }
    response = await ac.post("/api/v1/users/login", data=login_data)
    assert response.status_code == 200
    tokens = response.json()
    assert "access_token" in tokens
    access_token = tokens["access_token"]
    headers = {"Authorization": f"Bearer {access_token}"}

    # 3. Get Profile
    response = await ac.get("/api/v1/users/profile", headers=headers)
    assert response.status_code == 200
    assert response.json()["email"] == email

    # 4. Create Item
    item_data = {
        "name": "Integration Test Item",
        "category": "Testing"
    }
    response = await ac.post("/api/v1/items/", json=item_data, headers=headers)
    assert response.status_code == 201
    item = response.json()
    item_id = item["id"]
    assert item["name"] == item_data["name"]

    # 5. Get Item
    response = await ac.get(f"/api/v1/items/{item_id}", headers=headers)
    assert response.status_code == 200
    assert response.json()["id"] == item_id

    # 6. Update Item
    update_data = {"name": "Updated Name"}
    response = await ac.put(f"/api/v1/items/{item_id}", json=update_data, headers=headers)
    assert response.status_code == 200
    assert response.json()["name"] == "Updated Name"

    # 7. Analytics Check
    response = await ac.get("/api/v1/items/analytics/category-density", headers=headers)
    assert response.status_code == 200
    assert response.json()["success"] is True

    # 8. Delete Item
    response = await ac.delete(f"/api/v1/items/{item_id}", headers=headers)
    assert response.status_code == 200
    assert response.json()["status"] == "inactive"
    
    # Verify Soft Delete logic (Should still show up in DB but marked as deleted, 
    # but depending on GET implementation it might be filtered out. 
    # Our requirement says 'soft delete', and usually GET list filters them out.)
    # Let's check listing
    response = await ac.get("/api/v1/items/", headers=headers)
    assert response.status_code == 200
    # The deleted item should NOT be in the list ideally, or filtered.
    # Our implementation filters by deleted_at is None.
    items = response.json().get('items', []) # Paginated response now!
    assert not any(i["id"] == item_id for i in items)

@pytest.mark.asyncio
async def test_advanced_scenarios(ac: AsyncClient):
    # Setup: Create a user
    email = random_email()
    password = "securepassword123"
    register_data = {"email": email, "password": password, "first_name": "Adv", "last_name": "User"}
    await ac.post("/api/v1/users/register", json=register_data)
    
    # Login
    login_resp = await ac.post("/api/v1/users/login", data={"username": email, "password": password})
    token = login_resp.json()["access_token"]
    headers = {"Authorization": f"Bearer {token}"}
    
    # 1. Test Invalid UUID
    invalid_id = "not-a-uuid"
    resp = await ac.get(f"/api/v1/items/{invalid_id}", headers=headers)
    assert resp.status_code == 422 # Validation Error

    # 2. Test Non-existent Item
    random_id = uuid.uuid4()
    resp = await ac.get(f"/api/v1/items/{random_id}", headers=headers)
    assert resp.status_code == 404
    
    # 3. Analytics with Multiple Items
    # Create 3 items in 'Electronics', 1 in 'Books'
    for _ in range(3):
        await ac.post("/api/v1/items/", headers=headers, json={"name": "Phone", "category": "Electronics"})
    await ac.post("/api/v1/items/", headers=headers, json={"name": "Book", "category": "Books"})
    
    resp = await ac.get("/api/v1/items/analytics/category-density", headers=headers)
    assert resp.status_code == 200
    data = resp.json()["data"]
    
    # Verify Density Calculation
    # Note: Since tests run against the same DB, other items might exist. 
    # We check if categories exist and have valid percentages.
    categories = {c["category"]: c["percentage"] for c in data["categories"]}
    assert "Electronics" in categories
    assert "Books" in categories
    assert categories["Electronics"] > 0
    assert categories["Books"] > 0
    
    # 4. Inactive User Login Attempt (Simulated)
    # Since we don't have an endpoint to deactivate user easily without DB access in tests (unless we add one or mocking),
    # we will skip direct inactive login test OR rely on unit tests if we had user service.
    # However, we can try to access with an expired token signature if we could generate one, 
    # but that's complex without internal helpers exposed.
    # We'll stick to what we can test black-box style effectively.
