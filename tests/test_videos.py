"""
Video tests.
"""
import pytest
from httpx import AsyncClient


@pytest.mark.video
@pytest.mark.unit
class TestVideos:
    """Test video endpoints."""
    
    async def test_create_video(self, client: AsyncClient, auth_headers, test_channel):
        """Test video creation."""
        response = await client.post(
            "/api/v1/videos/",
            headers=auth_headers,
            json={
                "title": "New Video",
                "description": "A new video",
                "youtube_id": "dQw4w9WgXcQ",
                "channel_id": test_channel.id,
                "duration": 300
            }
        )
        assert response.status_code == 201
        data = response.json()
        assert data["status"] is True
        assert data["data"]["title"] == "New Video"
        assert data["data"]["youtube_id"] == "dQw4w9WgXcQ"
        assert "id" in data["data"]
    
    async def test_create_duplicate_youtube_id(self, client: AsyncClient, auth_headers, test_channel, test_video):
        """Test creating video with duplicate YouTube ID."""
        response = await client.post(
            "/api/v1/videos/",
            headers=auth_headers,
            json={
                "title": "Different Title",
                "youtube_id": "dQw4w9WgXcQ",
                "channel_id": test_channel.id
            }
        )
        assert response.status_code == 409
        data = response.json()
        assert data["status"] is False
    
    async def test_create_video_invalid_youtube_id(self, client: AsyncClient, auth_headers, test_channel):
        """Test creating video with invalid YouTube ID."""
        response = await client.post(
            "/api/v1/videos/",
            headers=auth_headers,
            json={
                "title": "Invalid Video",
                "youtube_id": "tooshort",
                "channel_id": test_channel.id
            }
        )
        assert response.status_code == 422  # Validation error
    
    async def test_list_videos(self, client: AsyncClient, test_video):
        """Test listing videos."""
        response = await client.get("/api/v1/videos/")
        assert response.status_code == 200
        data = response.json()
        assert data["status"] is True
        assert isinstance(data["data"], list)
        assert data["count"] > 0
    
    async def test_get_video_by_id(self, client: AsyncClient, test_video):
        """Test getting video by ID."""
        response = await client.get(f"/api/v1/videos/{test_video.id}")
        assert response.status_code == 200
        data = response.json()
        assert data["status"] is True
        assert data["data"]["id"] == test_video.id
        assert data["data"]["title"] == "Test Video"
    
    async def test_get_video_by_youtube_id(self, client: AsyncClient, test_video):
        """Test getting video by YouTube ID."""
        response = await client.get(f"/api/v1/videos/youtube/{test_video.youtube_id}")
        assert response.status_code == 200
        data = response.json()
        assert data["status"] is True
        assert data["data"]["youtube_id"] == "dQw4w9WgXcQ"
    
    async def test_get_video_not_found(self, client: AsyncClient):
        """Test getting non-existent video."""
        response = await client.get("/api/v1/videos/99999")
        assert response.status_code == 404
        data = response.json()
        assert data["status"] is False
    
    async def test_update_video(self, client: AsyncClient, auth_headers, test_video):
        """Test updating video."""
        response = await client.put(
            f"/api/v1/videos/{test_video.id}",
            headers=auth_headers,
            json={
                "title": "Updated Video",
                "view_count": 5000
            }
        )
        assert response.status_code == 200
        data = response.json()
        assert data["status"] is True
        assert data["data"]["title"] == "Updated Video"
        assert data["data"]["view_count"] == 5000
    
    async def test_delete_video(self, client: AsyncClient, auth_headers, test_video):
        """Test deleting video."""
        response = await client.delete(
            f"/api/v1/videos/{test_video.id}",
            headers=auth_headers
        )
        assert response.status_code == 200
        data = response.json()
        assert data["status"] is True
        
        # Verify video is deleted
        response = await client.get(f"/api/v1/videos/{test_video.id}")
        assert response.status_code == 404
    
    async def test_increment_view_count(self, client: AsyncClient, test_video):
        """Test incrementing view count."""
        initial_views = test_video.view_count
        
        response = await client.post(f"/api/v1/videos/{test_video.id}/view")
        assert response.status_code == 200
        data = response.json()
        assert data["status"] is True
        assert data["data"]["view_count"] == initial_views + 1
    
    async def test_filter_videos_by_channel(self, client: AsyncClient, test_video, test_channel):
        """Test filtering videos by channel."""
        response = await client.get(f"/api/v1/videos/?channel_id={test_channel.id}")
        assert response.status_code == 200
        data = response.json()
        assert data["status"] is True
        assert all(v["channel_id"] == test_channel.id for v in data["data"])
    
    async def test_filter_videos_by_active_status(self, client: AsyncClient, test_video):
        """Test filtering videos by active status."""
        response = await client.get("/api/v1/videos/?is_active=true")
        assert response.status_code == 200
        data = response.json()
        assert data["status"] is True
        assert all(v["is_active"] is True for v in data["data"])
    
    async def test_video_pagination(self, client: AsyncClient, test_channel, auth_headers):
        """Test video pagination."""
        # Create multiple videos
        youtube_ids = [f"{'a' * 11}{i}"[:11] for i in range(5)]
        for yt_id in youtube_ids:
            await client.post(
                "/api/v1/videos/",
                headers=auth_headers,
                json={
                    "title": f"Video {yt_id}",
                    "youtube_id": yt_id,
                    "channel_id": test_channel.id
                }
            )
        
        # Test pagination
        response = await client.get("/api/v1/videos/?skip=0&limit=3")
        assert response.status_code == 200
        data = response.json()
        assert data["status"] is True
        assert len(data["data"]) == 3
