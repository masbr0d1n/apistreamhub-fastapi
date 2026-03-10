"""
Streaming service - business logic for streaming control.
"""
from datetime import datetime
from typing import Optional
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select, update
import logging

from app.models.channel import Channel
from app.core.exceptions import StreamHubException
from app.config import settings


logger = logging.getLogger(__name__)


class StreamingService:
    """Service for managing channel streaming operations."""
    
    async def turn_on_air(
        self,
        db: AsyncSession,
        channel_id: int,
        user_id: int
    ) -> dict:
        """
        Turn on channel for streaming.
        
        Args:
            db: Database session
            channel_id: Channel ID to turn on
            user_id: User ID performing the action
            
        Returns:
            Dict with streaming status
            
        Raises:
            StreamHubException: If channel not found or already on-air
        """
        # Check if channel exists
        result = await db.execute(
            select(Channel).where(Channel.id == channel_id)
        )
        channel = result.scalar_one_or_none()
        
        if not channel:
            raise StreamHubException(
                message=f"Channel {channel_id} not found",
                statusCode=404
            )
        
        # Check if already on-air
        if channel.is_on_air:
            raise StreamHubException(
                message=f"Channel {channel_id} is already on-air",
                statusCode=400
            )
        
        # Update channel status
        await db.execute(
            update(Channel)
            .where(Channel.id == channel_id)
            .values(
                is_on_air=True,
                started_streaming_at=datetime.utcnow()
            )
        )
        await db.commit()
        
        # TODO: Integrate with actual streaming server (nginx-rtmp/ffmpeg)
        # For now, just update database status
        logger.info(f"Channel {channel_id} turned on by user {user_id}")
        
        return {
            "channel_id": channel_id,
            "status": "on-air",
            "started_at": datetime.utcnow(),
            "stream_url": f"rtmp://{settings.RTMP_STREAM_HOST}/live/{channel.name}",
            "message": f"Channel {channel.name} is now streaming"
        }
    
    async def turn_off_air(
        self,
        db: AsyncSession,
        channel_id: int,
        user_id: int
    ) -> dict:
        """
        Turn off channel streaming.
        
        Args:
            db: Database session
            channel_id: Channel ID to turn off
            user_id: User ID performing the action
            
        Returns:
            Dict with streaming status
            
        Raises:
            StreamHubException: If channel not found or already off-air
        """
        # Check if channel exists
        result = await db.execute(
            select(Channel).where(Channel.id == channel_id)
        )
        channel = result.scalar_one_or_none()
        
        if not channel:
            raise StreamHubException(
                message=f"Channel {channel_id} not found",
                statusCode=404
            )
        
        # Check if already off-air
        if not channel.is_on_air:
            raise StreamHubException(
                message=f"Channel {channel_id} is already off-air",
                statusCode=400
            )
        
        # Update channel status
        await db.execute(
            update(Channel)
            .where(Channel.id == channel_id)
            .values(
                is_on_air=False,
                stopped_streaming_at=datetime.utcnow()
            )
        )
        await db.commit()
        
        # TODO: Integrate with actual streaming server (nginx-rtmp/ffmpeg)
        # For now, just update database status
        logger.info(f"Channel {channel_id} turned off by user {user_id}")
        
        return {
            "channel_id": channel_id,
            "status": "off-air",
            "stopped_at": datetime.utcnow(),
            "message": f"Channel {channel.name} has stopped streaming"
        }
    
    async def get_status(
        self,
        db: AsyncSession,
        channel_id: int
    ) -> dict:
        """
        Get current streaming status of a channel.
        
        Args:
            db: Database session
            channel_id: Channel ID to check
            
        Returns:
            Dict with current streaming status
            
        Raises:
            StreamHubException: If channel not found
        """
        # Check if channel exists
        result = await db.execute(
            select(Channel).where(Channel.id == channel_id)
        )
        channel = result.scalar_one_or_none()
        
        if not channel:
            raise StreamHubException(
                message=f"Channel {channel_id} not found",
                statusCode=404
            )
        
        status_str = "on-air" if channel.is_on_air else "off-air"
        
        return {
            "channel_id": channel_id,
            "status": status_str,
            "started_at": channel.started_streaming_at,
            "stopped_at": channel.stopped_streaming_at,
            "stream_url": f"rtmp://{settings.RTMP_STREAM_HOST}/live/{channel.name}" if channel.is_on_air else None
        }
