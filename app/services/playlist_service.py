"""
Playlist service - business logic for playlist operations.
"""
from typing import List, Optional
from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from app.models.playlist import Playlist, PlaylistVideo
from app.models.channel import Channel
from app.models.video import Video
from app.schemas.playlist import PlaylistCreate, PlaylistUpdate
from app.core.exceptions import NotFoundException, ForbiddenException


class PlaylistService:
    """Service for playlist operations."""
    
    async def get_all(self, db: AsyncSession, skip: int = 0, limit: int = 100) -> List[Playlist]:
        """
        Get all playlists with pagination.
        
        Args:
            db: Database session
            skip: Number of records to skip
            limit: Maximum number of records to return
            
        Returns:
            List of playlists
        """
        result = await db.execute(
            select(Playlist)
            .offset(skip)
            .limit(limit)
            .order_by(Playlist.created_at.desc())
        )
        return list(result.scalars().all())
    
    async def get_by_id(self, db: AsyncSession, playlist_id: int) -> Playlist:
        """
        Get playlist by ID.
        
        Args:
            db: Database session
            playlist_id: Playlist ID
            
        Returns:
            Playlist object
            
        Raises:
            NotFoundException: If playlist not found
        """
        result = await db.execute(
            select(Playlist).where(Playlist.id == playlist_id)
        )
        playlist = result.scalar_one_or_none()
        
        if not playlist:
            raise NotFoundException(f"Playlist with ID {playlist_id} not found")
        
        return playlist
    
    async def get_by_channel(self, db: AsyncSession, channel_id: int) -> List[Playlist]:
        """
        Get all playlists for a specific channel.
        
        Args:
            db: Database session
            channel_id: Channel ID
            
        Returns:
            List of playlists
        """
        result = await db.execute(
            select(Playlist)
            .where(Playlist.channel_id == channel_id)
            .order_by(Playlist.created_at.desc())
        )
        return list(result.scalars().all())
    
    async def create(self, db: AsyncSession, playlist_data: PlaylistCreate, user_id: int) -> Playlist:
        """
        Create a new playlist.
        
        Args:
            db: Database session
            playlist_data: Playlist creation data
            user_id: User ID for ownership check
            
        Returns:
            Created playlist
            
        Raises:
            NotFoundException: If channel not found
            ForbiddenException: If user doesn't own the channel
        """
        # Verify channel exists and belongs to user
        channel_result = await db.execute(
            select(Channel).where(Channel.id == playlist_data.channel_id)
        )
        channel = channel_result.scalar_one_or_none()
        
        if not channel:
            raise NotFoundException("Channel not found")
        
        # Check if channel belongs to user (assuming channel has user_id field)
        # Note: This check depends on your Channel model structure
        # if hasattr(channel, 'user_id') and channel.user_id != user_id:
        #     raise ForbiddenException("You don't own this channel")
        
        # Create playlist
        playlist = Playlist(
            name=playlist_data.name,
            channel_id=playlist_data.channel_id,
            start_time=playlist_data.start_time,
            description=playlist_data.description
        )
        
        db.add(playlist)
        await db.commit()
        await db.refresh(playlist)
        
        return playlist
    
    async def update(self, db: AsyncSession, playlist_id: int, playlist_data: PlaylistUpdate, user_id: int) -> Playlist:
        """
        Update a playlist.
        
        Args:
            db: Database session
            playlist_id: Playlist ID
            playlist_data: Playlist update data
            user_id: User ID for ownership check
            
        Returns:
            Updated playlist
            
        Raises:
            NotFoundException: If playlist not found
            ForbiddenException: If user doesn't own the playlist
        """
        playlist = await self.get_by_id(db, playlist_id)
        
        # Check ownership (through channel)
        channel_result = await db.execute(
            select(Channel).where(Channel.id == playlist.channel_id)
        )
        channel = channel_result.scalar_one_or_none()
        
        # if hasattr(channel, 'user_id') and channel.user_id != user_id:
        #     raise ForbiddenException("You don't own this playlist")
        
        # Update fields
        update_data = playlist_data.model_dump(exclude_unset=True)
        for field, value in update_data.items():
            setattr(playlist, field, value)
        
        await db.commit()
        await db.refresh(playlist)
        
        return playlist
    
    async def delete(self, db: AsyncSession, playlist_id: int, user_id: int) -> None:
        """
        Delete a playlist.
        
        Args:
            db: Database session
            playlist_id: Playlist ID
            user_id: User ID for ownership check
            
        Raises:
            NotFoundException: If playlist not found
            ForbiddenException: If user doesn't own the playlist
        """
        playlist = await self.get_by_id(db, playlist_id)
        
        # Check ownership (through channel)
        channel_result = await db.execute(
            select(Channel).where(Channel.id == playlist.channel_id)
        )
        channel = channel_result.scalar_one_or_none()
        
        # if hasattr(channel, 'user_id') and channel.user_id != user_id:
        #     raise ForbiddenException("You don't own this playlist")
        
        await db.delete(playlist)
        await db.commit()
    
    async def add_video(self, db: AsyncSession, playlist_id: int, video_id: int, order: int = 0) -> PlaylistVideo:
        """
        Add a video to a playlist.
        
        Args:
            db: Database session
            playlist_id: Playlist ID
            video_id: Video ID
            order: Video order in playlist
            
        Returns:
            Created playlist-video relation
            
        Raises:
            NotFoundException: If playlist or video not found
        """
        # Verify playlist exists
        playlist_result = await db.execute(
            select(Playlist).where(Playlist.id == playlist_id)
        )
        playlist = playlist_result.scalar_one_or_none()
        
        if not playlist:
            raise NotFoundException("Playlist not found")
        
        # Verify video exists
        video_result = await db.execute(
            select(Video).where(Video.id == video_id)
        )
        video = video_result.scalar_one_or_none()
        
        if not video:
            raise NotFoundException("Video not found")
        
        # Create playlist-video relation
        playlist_video = PlaylistVideo(
            playlist_id=playlist_id,
            video_id=video_id,
            order=order
        )
        
        db.add(playlist_video)
        
        # Update video count
        playlist.video_count += 1
        
        await db.commit()
        await db.refresh(playlist_video)
        
        return playlist_video
    
    async def remove_video(self, db: AsyncSession, playlist_id: int, video_id: int) -> None:
        """
        Remove a video from a playlist.
        
        Args:
            db: Database session
            playlist_id: Playlist ID
            video_id: Video ID
            
        Raises:
            NotFoundException: If playlist-video relation not found
        """
        result = await db.execute(
            select(PlaylistVideo).where(
                PlaylistVideo.playlist_id == playlist_id,
                PlaylistVideo.video_id == video_id
            )
        )
        playlist_video = result.scalar_one_or_none()
        
        if not playlist_video:
            raise NotFoundException("Video not in playlist")
        
        # Get playlist to update count
        playlist_result = await db.execute(
            select(Playlist).where(Playlist.id == playlist_id)
        )
        playlist = playlist_result.scalar_one_or_none()
        
        if playlist:
            playlist.video_count = max(0, playlist.video_count - 1)
        
        await db.delete(playlist_video)
        await db.commit()
    
    async def get_videos(self, db: AsyncSession, playlist_id: int) -> List[PlaylistVideo]:
        """
        Get all videos in a playlist.
        
        Args:
            db: Database session
            playlist_id: Playlist ID
            
        Returns:
            List of playlist-video relations
        """
        result = await db.execute(
            select(PlaylistVideo)
            .where(PlaylistVideo.playlist_id == playlist_id)
            .order_by(PlaylistVideo.order)
        )
        return list(result.scalars().all())
    
    async def clear_videos(self, db: AsyncSession, playlist_id: int) -> None:
        """
        Clear all videos from a playlist.
        
        Args:
            db: Database session
            playlist_id: Playlist ID
        """
        # Get all playlist videos
        result = await db.execute(
            select(PlaylistVideo).where(PlaylistVideo.playlist_id == playlist_id)
        )
        playlist_videos = result.scalars().all()
        
        # Delete all
        for pv in playlist_videos:
            await db.delete(pv)
        
        # Update playlist video count
        playlist_result = await db.execute(
            select(Playlist).where(Playlist.id == playlist_id)
        )
        playlist = playlist_result.scalar_one_or_none()
        
        if playlist:
            playlist.video_count = 0
        
        await db.commit()
