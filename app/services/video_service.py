"""
Video service - business logic for video operations.
"""
from typing import List, Optional
from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from app.models.video import Video
from app.schemas.video import VideoCreate, VideoUpdate
from app.core.exceptions import NotFoundException, ConflictException


class VideoService:
    """Service for video operations."""
    
    async def get_all(
        self,
        db: AsyncSession,
        skip: int = 0,
        limit: int = 100,
        channel_id: Optional[int] = None,
        is_active: Optional[bool] = None
    ) -> List[Video]:
        """
        Get all videos with optional filtering.
        
        Args:
            db: Database session
            skip: Number of records to skip
            limit: Maximum number of records to return
            channel_id: Filter by channel ID
            is_active: Filter by active status
            
        Returns:
            List of videos
        """
        query = select(Video)
        
        # Apply filters
        if channel_id is not None:
            query = query.where(Video.channel_id == channel_id)
        if is_active is not None:
            query = query.where(Video.is_active == is_active)
        
        # Apply pagination and ordering
        query = query.offset(skip).limit(limit).order_by(Video.created_at.desc())
        
        result = await db.execute(query)
        return list(result.scalars().all())
    
    async def get_by_id(self, db: AsyncSession, video_id: int) -> Video:
        """
        Get video by ID.
        
        Args:
            db: Database session
            video_id: Video ID
            
        Returns:
            Video object
            
        Raises:
            NotFoundException: If video not found
        """
        result = await db.execute(
            select(Video).where(Video.id == video_id)
        )
        video = result.scalar_one_or_none()
        
        if not video:
            raise NotFoundException(f"Video with ID {video_id} not found")
        
        return video
    
    async def get_by_youtube_id(self, db: AsyncSession, youtube_id: str) -> Optional[Video]:
        """
        Get video by YouTube ID.
        
        Args:
            db: Database session
            youtube_id: YouTube video ID
            
        Returns:
            Video object or None
        """
        result = await db.execute(
            select(Video).where(Video.youtube_id == youtube_id)
        )
        return result.scalar_one_or_none()
    
    async def create(self, db: AsyncSession, video_data: VideoCreate) -> Video:
        """
        Create a new video.
        
        Args:
            db: Database session
            video_data: Video creation data
            
        Returns:
            Created video
            
        Raises:
            ConflictException: If video already exists
        """
        # Check if YouTube ID already exists
        existing = await self.get_by_youtube_id(db, video_data.youtube_id)
        if existing:
            raise ConflictException(f"Video with YouTube ID '{video_data.youtube_id}' already exists")
        
        # Create new video
        video = Video(**video_data.model_dump())
        db.add(video)
        await db.commit()
        await db.refresh(video)
        
        return video
    
    async def update(
        self,
        db: AsyncSession,
        video_id: int,
        video_data: VideoUpdate
    ) -> Video:
        """
        Update a video.
        
        Args:
            db: Database session
            video_id: Video ID
            video_data: Video update data
            
        Returns:
            Updated video
            
        Raises:
            NotFoundException: If video not found
        """
        video = await self.get_by_id(db, video_id)
        
        # Update fields
        update_data = video_data.model_dump(exclude_unset=True)
        for field, value in update_data.items():
            setattr(video, field, value)
        
        await db.commit()
        await db.refresh(video)
        
        return video
    
    async def delete(self, db: AsyncSession, video_id: int) -> bool:
        """
        Delete a video.
        
        Args:
            db: Database session
            video_id: Video ID
            
        Returns:
            True if deleted
            
        Raises:
            NotFoundException: If video not found
        """
        video = await self.get_by_id(db, video_id)
        
        await db.delete(video)
        await db.commit()
        
        return True
    
    async def increment_view_count(self, db: AsyncSession, video_id: int) -> Video:
        """
        Increment video view count.
        
        Args:
            db: Database session
            video_id: Video ID
            
        Returns:
            Updated video
            
        Raises:
            NotFoundException: If video not found
        """
        video = await self.get_by_id(db, video_id)
        video.view_count += 1
        await db.commit()
        await db.refresh(video)
        
        return video
