"""
Channel tests.
"""
import pytest
from httpx import AsyncClient


@pytest.mark.channel
@pytest.mark.unit
class TestChannels:
    """Test channel endpoints."""
    
    async def test_create_channel(self, client: AsyncClient, auth_headers):
        """Test channel creation."""
        response = await client.post(
            "/api/v1/channels/create-channel",
            headers=auth_headers,
            json={
                "name": "New Channel",
                "category": "sport",
                "description": "A new channel"
            }
        )
        assert response.status_code == 201
        data = response.json()
        assert data["status"] is True
        assert data["data"]["name"] == "New Channel"
        assert data["data"]["category"] == "sport"
        assert "id" in data["data"]
    
    async def test_create_duplicate_channel(self, client: AsyncClient, auth_headers, test_channel):
        """Test creating duplicate channel."""
        response = await client.post(
            "/api/v1/channels/create-channel",
            headers=auth_headers,
            json={
                "name": "Test Channel",
                "category": "entertainment"
            }
        )
        assert response.status_code == 409
        data = response.json()
        assert data["status"] is False
    
    async def test_list_channels(self, client: AsyncClient, test_channel):
        """Test listing channels."""
        response = await client.get("/api/v1/channels/")
        assert response.status_code == 200
        data = response.json()
        assert data["status"] is True
        assert isinstance(data["data"], list)
        assert data["count"] > 0
    
    async def test_get_channel_by_id(self, client: AsyncClient, test_channel):
        """Test getting channel by ID."""
        response = await client.get(f"/api/v1/channels/{test_channel.id}")
        assert response.status_code == 200
        data = response.json()
        assert data["status"] is True
        assert data["data"]["id"] == test_channel.id
        assert data["data"]["name"] == "Test Channel"
    
    async def test_get_channel_not_found(self, client: AsyncClient):
        """Test getting non-existent channel."""
        response = await client.get("/api/v1/channels/99999")
        assert response.status_code == 404
        data = response.json()
        assert data["status"] is False
    
    async def test_update_channel(self, client: AsyncClient, auth_headers, test_channel):
        """Test updating channel."""
        response = await client.put(
            f"/api/v1/channels/{test_channel.id}",
            headers=auth_headers,
            json={
                "name": "Updated Channel",
                "category": "gaming"
            }
        )
        assert response.status_code == 200
        data = response.json()
        assert data["status"] is True
        assert data["data"]["name"] == "Updated Channel"
        assert data["data"]["category"] == "gaming"
    
    async def test_update_channel_not_found(self, client: AsyncClient, auth_headers):
        """Test updating non-existent channel."""
        response = await client.put(
            "/api/v1/channels/99999",
            headers=auth_headers,
            json={"name": "Updated"}
        )
        assert response.status_code == 404
        data = response.json()
        assert data["status"] is False
    
    async def test_delete_channel(self, client: AsyncClient, auth_headers, test_channel):
        """Test deleting channel."""
        response = await client.delete(
            f"/api/v1/channels/{test_channel.id}",
            headers=auth_headers
        )
        assert response.status_code == 200
        data = response.json()
        assert data["status"] is True
        
        # Verify channel is deleted
        response = await client.get(f"/api/v1/channels/{test_channel.id}")
        assert response.status_code == 404
    
    async def test_delete_channel_not_found(self, client: AsyncClient, auth_headers):
        """Test deleting non-existent channel."""
        response = await client.delete(
            "/api/v1/channels/99999",
            headers=auth_headers
        )
        assert response.status_code == 404
        data = response.json()
        assert data["status"] is False
    
    async def test_channel_pagination(self, client: AsyncClient):
        """Test channel pagination."""
        # Create multiple channels
        for i in range(5):
            await client.post(
                "/api/v1/channels/create-channel",
                headers=await self._get_auth_header(client),
                json={
                    "name": f"Channel {i}",
                    "category": "entertainment"
                }
            )
        
        # Test pagination
        response = await client.get("/api/v1/channels/?skip=0&limit=3")
        assert response.status_code == 200
        data = response.json()
        assert data["status"] is True
        assert len(data["data"]) == 3
    
    async def _get_auth_header(self, client: AsyncClient) -> dict:
        """Helper to get auth header."""
        response = await client.post(
            "/api/v1/auth/register",
            json={
                "username": "tempuser",
                "email": "temp@example.com",
                "full_name": "Temp",
                "password": "password123"
            }
        )
        response = await client.post(
            "/api/v1/auth/login",
            json={"username": "tempuser", "password": "password123"}
        )
        token = response.json()["data"]["access_token"]
        return {"Authorization": f"Bearer {token}"}
