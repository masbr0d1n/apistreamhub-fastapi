"""
Channel service - business logic for channel operations.
"""
from typing import List, Optional
from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from app.models.channel import Channel
from app.schemas.channel import ChannelCreate, ChannelUpdate
from app.core.exceptions import NotFoundException, ConflictException


class ChannelService:
    """Service for channel operations."""
    
    async def get_all(self, db: AsyncSession, skip: int = 0, limit: int = 100) -> List[Channel]:
        """
        Get all channels with pagination.
        
        Args:
            db: Database session
            skip: Number of records to skip
            limit: Maximum number of records to return
            
        Returns:
            List of channels
        """
        result = await db.execute(
            select(Channel)
            .offset(skip)
            .limit(limit)
            .order_by(Channel.name)
        )
        return list(result.scalars().all())
    
    async def get_by_id(self, db: AsyncSession, channel_id: int) -> Channel:
        """
        Get channel by ID.
        
        Args:
            db: Database session
            channel_id: Channel ID
            
        Returns:
            Channel object
            
        Raises:
            NotFoundException: If channel not found
        """
        result = await db.execute(
            select(Channel).where(Channel.id == channel_id)
        )
        channel = result.scalar_one_or_none()
        
        if not channel:
            raise NotFoundException(f"Channel with ID {channel_id} not found")
        
        return channel
    
    async def get_by_name(self, db: AsyncSession, name: str) -> Optional[Channel]:
        """
        Get channel by name.
        
        Args:
            db: Database session
            name: Channel name
            
        Returns:
            Channel object or None
        """
        result = await db.execute(
            select(Channel).where(Channel.name == name)
        )
        return result.scalar_one_or_none()
    
    async def create(self, db: AsyncSession, channel_data: ChannelCreate) -> Channel:
        """
        Create a new channel.
        
        Args:
            db: Database session
            channel_data: Channel creation data
            
        Returns:
            Created channel
            
        Raises:
            ConflictException: If channel already exists
        """
        # Check if channel already exists
        existing = await self.get_by_name(db, channel_data.name)
        if existing:
            raise ConflictException(f"Channel '{channel_data.name}' already exists")
        
        # Create new channel
        channel = Channel(**channel_data.model_dump())
        db.add(channel)
        await db.commit()
        await db.refresh(channel)
        
        return channel
    
    async def update(
        self,
        db: AsyncSession,
        channel_id: int,
        channel_data: ChannelUpdate
    ) -> Channel:
        """
        Update a channel.
        
        Args:
            db: Database session
            channel_id: Channel ID
            channel_data: Channel update data
            
        Returns:
            Updated channel
            
        Raises:
            NotFoundException: If channel not found
        """
        channel = await self.get_by_id(db, channel_id)
        
        # Update fields
        update_data = channel_data.model_dump(exclude_unset=True)
        for field, value in update_data.items():
            setattr(channel, field, value)
        
        await db.commit()
        await db.refresh(channel)
        
        return channel
    
    async def delete(self, db: AsyncSession, channel_id: int) -> bool:
        """
        Delete a channel.
        
        Args:
            db: Database session
            channel_id: Channel ID
            
        Returns:
            True if deleted
            
        Raises:
            NotFoundException: If channel not found
        """
        channel = await self.get_by_id(db, channel_id)
        
        await db.delete(channel)
        await db.commit()
        
        return True
