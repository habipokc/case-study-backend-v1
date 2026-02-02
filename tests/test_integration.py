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
    response = await ac.post("/api/v1/auth/register", json=register_data)
    assert response.status_code == 201
    user_id = response.json()["id"]

    # 2. Login
    login_data = {
        "username": email,
        "password": password
    }
    response = await ac.post("/api/v1/auth/login", data=login_data)
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
    items = response.json()
    assert not any(i["id"] == item_id for i in items)
