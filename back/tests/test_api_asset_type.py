import uuid
import pytest

@pytest.mark.asyncio
async def test_create_asset_type(async_client):
    await async_client.post("/api/v1/auth/register", data={"username": "assettype@example.com", "password": "topsecret123"})
    login = await async_client.post(
        "/api/v1/auth/token", data={"username": "assettype@example.com", "password": "topsecret123"}
    )
    token = login.json()["access_token"]
    headers = {"Authorization": f"Bearer {token}"}

    resp = await async_client.post("/api/v1/asset_type/", json={"name": "Equity"}, headers=headers)
    assert resp.status_code == 201
    assert resp.json()["name"] == "Equity"


@pytest.mark.asyncio
async def test_list_asset_types(async_client):
    await async_client.post("/api/v1/auth/register", data={"username": "assettype2@example.com", "password": "topsecret123"})
    login = await async_client.post(
        "/api/v1/auth/token", data={"username": "assettype2@example.com", "password": "topsecret123"}
    )
    token = login.json()["access_token"]
    headers = {"Authorization": f"Bearer {token}"}

    resp = await async_client.get("/api/v1/asset_type/", headers=headers)
    assert resp.status_code == 200
    assert isinstance(resp.json(), list)


@pytest.mark.asyncio
async def test_get_update_delete_asset_type(async_client):
    await async_client.post("/api/v1/auth/register", data={"username": "assettype3@example.com", "password": "topsecret123"})
    login = await async_client.post(
        "/api/v1/auth/token", data={"username": "assettype3@example.com", "password": "topsecret123"}
    )
    token = login.json()["access_token"]
    headers = {"Authorization": f"Bearer {token}"}

    create_resp = await async_client.post("/api/v1/asset_type/", json={"name": "Bond"}, headers=headers)
    assert create_resp.status_code == 201
    assert create_resp.status_code == 201
    asset_type = create_resp.json()
    asset_type_id = asset_type["id"]

    # GET
    get_resp = await async_client.get(f"/api/v1/asset_type/{asset_type_id}", headers=headers)
    assert get_resp.status_code == 200
    assert get_resp.json()["name"] == "Bond"

    # PUT
    update_resp = await async_client.put(
        f"/api/v1/asset_type/{asset_type_id}", json={"name": "Updated Bond"}, headers=headers
    )
    assert update_resp.status_code == 200
    assert update_resp.json()["name"] == "Updated Bond"

    # DELETE
    delete_resp = await async_client.delete(f"/api/v1/asset_type/{asset_type_id}", headers=headers)
    assert delete_resp.status_code == 204

    # GET after delete
    get_after_delete = await async_client.get(f"/api/v1/asset_type/{asset_type_id}", headers=headers)
    assert get_after_delete.status_code == 404


@pytest.mark.asyncio
async def test_unauthorized_asset_type_access(async_client):
    # Should return 401 without auth header
    resp = await async_client.get("/api/v1/asset_type/")
    assert resp.status_code in (401, 403)


@pytest.mark.asyncio
async def test_get_nonexistent_asset_type(async_client):
    await async_client.post("/api/v1/auth/register", data={"username": "miss@example.com", "password": "topsecret123"})
    login = await async_client.post("/api/v1/auth/token", data={"username": "miss@example.com", "password": "topsecret123"})
    token = login.json()["access_token"]
    headers = {"Authorization": f"Bearer {token}"}

    fake_id = str(uuid.uuid4())
    resp = await async_client.get(f"/api/v1/asset_type/{fake_id}", headers=headers)
    assert resp.status_code == 404
    assert "AssetType not found" in resp.text
