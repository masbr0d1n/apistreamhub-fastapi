"""
Streaming control tests.
"""
import pytest
from httpx import AsyncClient


class TestStreamingControl:
    """Test streaming control endpoints."""
    
    @pytest.mark.asyncio
    async def test_turn_on_air_success(self, async_client: AsyncClient, auth_headers: dict):
        """Test turning on channel for streaming."""
        # First create a channel
        channel_data = {
            "name": "Test Channel",
            "description": "Test channel for streaming",
            "category": "test"
        }
        
        # Create channel
        response = await async_client.post(
            "/api/v1/channels/",
            json=channel_data,
            headers=auth_headers
        )
        assert response.status_code == 201
        channel_id = response.json()["data"]["id"]
        
        # Turn on channel
        response = await async_client.post(
            f"/api/v1/streaming/channels/{channel_id}/on-air",
            headers=auth_headers
        )
        
        assert response.status_code == 200
        data = response.json()
        assert data["status"] is True
        assert data["data"]["status"] == "on-air"
        assert data["data"]["channel_id"] == channel_id
        assert "started_at" in data["data"]
    
    @pytest.mark.asyncio
    async def test_turn_off_air_success(self, async_client: AsyncClient, auth_headers: dict):
        """Test turning off channel streaming."""
        # Create and turn on channel
        channel_data = {
            "name": "Test Channel 2",
            "description": "Test channel 2",
            "category": "test"
        }
        
        response = await async_client.post(
            "/api/v1/channels/",
            json=channel_data,
            headers=auth_headers
        )
        channel_id = response.json()["data"]["id"]
        
        # Turn on
        await async_client.post(
            f"/api/v1/streaming/channels/{channel_id}/on-air",
            headers=auth_headers
        )
        
        # Turn off
        response = await async_client.post(
            f"/api/v1/streaming/channels/{channel_id}/off-air",
            headers=auth_headers
        )
        
        assert response.status_code == 200
        data = response.json()
        assert data["status"] is True
        assert data["data"]["status"] == "off-air"
        assert "stopped_at" in data["data"]
    
    @pytest.mark.asyncio
    async def test_get_channel_status(self, async_client: AsyncClient, auth_headers: dict):
        """Test getting channel streaming status."""
        # Create channel
        channel_data = {
            "name": "Test Channel 3",
            "description": "Test channel 3",
            "category": "test"
        }
        
        response = await async_client.post(
            "/api/v1/channels/",
            json=channel_data,
            headers=auth_headers
        )
        channel_id = response.json()["data"]["id"]
        
        # Get status
        response = await async_client.get(
            f"/api/v1/streaming/channels/{channel_id}/status",
            headers=auth_headers
        )
        
        assert response.status_code == 200
        data = response.json()
        assert data["status"] is True
        assert data["data"]["channel_id"] == channel_id
        assert data["data"]["status"] == "off-air"  # Default status
    
    @pytest.mark.asyncio
    async def test_turn_on_nonexistent_channel(self, async_client: AsyncClient, auth_headers: dict):
        """Test turning on non-existent channel."""
        response = await async_client.post(
            "/api/v1/streaming/channels/99999/on-air",
            headers=auth_headers
        )
        
        assert response.status_code == 404
        data = response.json()
        assert data["status"] is False
    
    @pytest.mark.asyncio
    async def test_turn_on_already_on_air(self, async_client: AsyncClient, auth_headers: dict):
        """Test turning on channel that's already on-air."""
        # Create channel
        channel_data = {
            "name": "Test Channel 4",
            "description": "Test channel 4",
            "category": "test"
        }
        
        response = await async_client.post(
            "/api/v1/channels/",
            json=channel_data,
            headers=auth_headers
        )
        channel_id = response.json()["data"]["id"]
        
        # Turn on once
        await async_client.post(
            f"/api/v1/streaming/channels/{channel_id}/on-air",
            headers=auth_headers
        )
        
        # Try to turn on again
        response = await async_client.post(
            f"/api/v1/streaming/channels/{channel_id}/on-air",
            headers=auth_headers
        )
        
        assert response.status_code == 400
        data = response.json()
        assert data["status"] is False
        assert "already on-air" in data["message"].lower()
    
    @pytest.mark.asyncio
    async def test_unauthorized_access(self, async_client: AsyncClient):
        """Test accessing streaming endpoints without authentication."""
        response = await async_client.post(
            "/api/v1/streaming/channels/1/on-air"
        )
        
        assert response.status_code == 401
