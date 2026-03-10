"""
Video service tests.
"""
import pytest
from sqlalchemy.ext.asyncio import AsyncSession

from app.schemas.video import VideoCreate, VideoUpdate
from app.services.video_service import VideoService
from app.models.video import Video
from app.core.exceptions import NotFoundException, ConflictException


@pytest.mark.unit
@pytest.mark.service
class TestVideoService:
    """Test VideoService business logic."""
    
    async def test_create_video_success(self, test_db: AsyncSession, test_channel):
        """Test successful video creation."""
        video_service = VideoService()
        video_data = VideoCreate(
            title="Test Video",
            description="A test video",
            youtube_id="dQw4w9WgXcQ",
            channel_id=test_channel.id
        )
        
        video = await video_service.create(test_db, video_data)
        
        assert video is not None
        assert video.title == "Test Video"
        assert video.youtube_id == "dQw4w9WgXcQ"
        assert video.channel_id == test_channel.id
    
    async def test_create_duplicate_youtube_id(self, test_db: AsyncSession, test_channel):
        """Test creating video with duplicate YouTube ID."""
        video_service = VideoService()
        
        # Create first video
        video_data1 = VideoCreate(
            title="First Video",
            youtube_id="unique123",
            channel_id=test_channel.id
        )
        await video_service.create(test_db, video_data1)
        
        # Try to create duplicate
        video_data2 = VideoCreate(
            title="Duplicate Video",
            youtube_id="unique123",
            channel_id=test_channel.id
        )
        
        with pytest.raises(ConflictException) as exc_info:
            await video_service.create(test_db, video_data2)
        
        assert "already exists" in str(exc_info.value)
    
    async def test_get_by_id(self, test_db: AsyncSession, test_channel):
        """Test getting video by ID."""
        video_service = VideoService()
        
        # Create a video
        video_data = VideoCreate(
            title="Get Video Test",
            youtube_id="gettest123",
            channel_id=test_channel.id
        )
        video = await video_service.create(test_db, video_data)
        
        # Retrieve it
        retrieved = await video_service.get_by_id(test_db, video.id)
        
        assert retrieved is not None
        assert retrieved.id == video.id
    
    async def test_get_by_id_not_found(self, test_db: AsyncSession):
        """Test getting non-existent video by ID."""
        video_service = VideoService()
        
        video = await video_service.get_by_id(test_db, 99999)
        
        assert video is None
    
    async def test_get_by_youtube_id(self, test_db: AsyncSession, test_channel):
        """Test getting video by YouTube ID."""
        video_service = VideoService()
        
        # Create a video
        video_data = VideoCreate(
            title="YouTube ID Test",
            youtube_id="youtubetest123",
            channel_id=test_channel.id
        )
        await video_service.create(test_db, video_data)
        
        # Retrieve by YouTube ID
        video = await video_service.get_by_youtube_id(test_db, "youtubetest123")
        
        assert video is not None
        assert video.youtube_id == "youtubetest123"
    
    async def test_get_by_youtube_id_not_found(self, test_db: AsyncSession):
        """Test getting non-existent video by YouTube ID."""
        video_service = VideoService()
        
        video = await video_service.get_by_youtube_id(test_db, "nonexistent")
        
        assert video is None
    
    async def test_get_all(self, test_db: AsyncSession, test_channel):
        """Test listing all videos."""
        video_service = VideoService()
        
        # Create multiple videos
        for i in range(5):
            video_data = VideoCreate(
                title=f"Video {i}",
                youtube_id=f"vid{i}test123",
                channel_id=test_channel.id
            )
            await video_service.create(test_db, video_data)
        
        videos = await video_service.get_all(test_db, skip=0, limit=10)
        
        assert len(videos) >= 5
    
    async def test_update_video(self, test_db: AsyncSession, test_channel):
        """Test updating video."""
        video_service = VideoService()
        
        # Create a video
        video_data = VideoCreate(
            title="Update Test",
            youtube_id="updatetest123",
            channel_id=test_channel.id
        )
        video = await video_service.create(test_db, video_data)
        
        # Update it
        update_data = VideoUpdate(
            title="Updated Title",
            description="Updated description"
        )
        updated = await video_service.update(test_db, video.id, update_data)
        
        assert updated is not None
        assert updated.title == "Updated Title"
        assert updated.description == "Updated description"
    
    async def test_update_video_not_found(self, test_db: AsyncSession):
        """Test updating non-existent video."""
        video_service = VideoService()
        
        update_data = VideoUpdate(title="New Title")
        
        with pytest.raises(NotFoundException):
            await video_service.update(test_db, 99999, update_data)
    
    async def test_delete_video(self, test_db: AsyncSession, test_channel):
        """Test deleting video."""
        video_service = VideoService()
        
        # Create a video
        video_data = VideoCreate(
            title="Delete Test",
            youtube_id="deletetest123",
            channel_id=test_channel.id
        )
        video = await video_service.create(test_db, video_data)
        
        # Delete it
        success = await video_service.delete(test_db, video.id)
        
        assert success is True
        
        # Verify it's deleted
        deleted_video = await video_service.get_by_id(test_db, video.id)
        assert deleted_video is None
    
    async def test_delete_video_not_found(self, test_db: AsyncSession):
        """Test deleting non-existent video."""
        video_service = VideoService()
        
        success = await video_service.delete(test_db, 99999)
        
        assert success is False
    
    async def test_increment_view_count(self, test_db: AsyncSession, test_channel):
        """Test incrementing view count."""
        video_service = VideoService()
        
        # Create a video
        video_data = VideoCreate(
            title="View Count Test",
            youtube_id="viewcount123",
            channel_id=test_channel.id
        )
        video = await video_service.create(test_db, video_data)
        
        initial_count = video.view_count
        
        # Increment view count
        updated = await video_service.increment_view_count(test_db, video.id)
        
        assert updated is not None
        assert updated.view_count == initial_count + 1
    
    async def test_increment_view_count_not_found(self, test_db: AsyncSession):
        """Test incrementing view count for non-existent video."""
        video_service = VideoService()
        
        updated = await video_service.increment_view_count(test_db, 99999)
        
        assert updated is None
    
    async def test_filter_by_channel(self, test_db: AsyncSession):
        """Test filtering videos by channel."""
        video_service = VideoService()
        
        # Create two channels
        from app.models.channel import Channel
        channel1 = Channel(name="Channel Filter 1", category="test1")
        channel2 = Channel(name="Channel Filter 2", category="test2")
        test_db.add_all([channel1, channel2])
        await test_db.commit()
        await test_db.refresh(channel1)
        await test_db.refresh(channel2)
        
        # Create videos for each channel
        for i in range(3):
            video_data = VideoCreate(
                title=f"Channel 1 Video {i}",
                youtube_id=f"c1vid{i}123",
                channel_id=channel1.id
            )
            await video_service.create(test_db, video_data)
        
        for i in range(2):
            video_data = VideoCreate(
                title=f"Channel 2 Video {i}",
                youtube_id=f"c2vid{i}123",
                channel_id=channel2.id
            )
            await video_service.create(test_db, video_data)
        
        # Filter by channel 1
        videos = await video_service.filter_by_channel(test_db, channel1.id)
        
        assert len(videos) == 3
    
    async def test_filter_by_active_status(self, test_db: AsyncSession, test_channel):
        """Test filtering videos by active status."""
        video_service = VideoService()
        
        # Create active and inactive videos
        for i in range(3):
            video_data = VideoCreate(
                title=f"Active Video {i}",
                youtube_id=f"active{i}123",
                channel_id=test_channel.id,
                is_active=True
            )
            await video_service.create(test_db, video_data)
        
        video_data = VideoCreate(
            title="Inactive Video",
            youtube_id="inactive123",
            channel_id=test_channel.id,
            is_active=False
        )
        await video_service.create(test_db, video_data)
        
        # Filter active videos
        active_videos = await video_service.filter_by_active_status(test_db, True)
        
        assert len(active_videos) == 3
        
        # Filter inactive videos
        inactive_videos = await video_service.filter_by_active_status(test_db, False)
        
        assert len(inactive_videos) == 1
    
    async def test_video_resolution_property(self, test_db: AsyncSession, test_channel):
        """Test video resolution property."""
        video_service = VideoService()
        
        video_data = VideoCreate(
            title="Resolution Test",
            youtube_id="restest123",
            channel_id=test_channel.id
        )
        video = await video_service.create(test_db, video_data)
        
        # Set dimensions
        video.width = 1920
        video.height = 1080
        await test_db.commit()
        
        assert video.resolution == "1920x1080"
    
    async def test_video_bitrate_properties(self, test_db: AsyncSession, test_channel):
        """Test video bitrate properties."""
        video_service = VideoService()
        
        video_data = VideoCreate(
            title="Bitrate Test",
            youtube_id="bittest123",
            channel_id=test_channel.id
        )
        video = await video_service.create(test_db, video_data)
        
        # Set bitrates
        video.video_bitrate = 5000000  # 5 Mbps
        video.audio_bitrate = 128000  # 128 kbps
        await test_db.commit()
        
        assert video.video_bitrate_mbps == 5.0
        assert video.audio_bitrate_kbps == 128.0
    
    async def test_video_properties_none(self, test_db: AsyncSession, test_channel):
        """Test video properties when values are None."""
        video_service = VideoService()
        
        video_data = VideoCreate(
            title="None Props Test",
            youtube_id="noneprops123",
            channel_id=test_channel.id
        )
        video = await video_service.create(test_db, video_data)
        
        assert video.resolution is None
        assert video.video_bitrate_mbps is None
        assert video.audio_bitrate_kbps is None
