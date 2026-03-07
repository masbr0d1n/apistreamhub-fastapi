"""
Screen service - business logic for Videotron device management.
"""
import uuid
from datetime import datetime
from typing import List, Optional
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select, update, delete
from sqlalchemy.orm import selectinload

from app.models.screen import Screen, ScreenStatus
from app.models.screen_group import ScreenGroup, ScreenGroupItem


class ScreenService:
    """Service class for Screen operations."""
    
    async def get_all(
        self,
        db: AsyncSession,
        skip: int = 0,
        limit: int = 100,
        status: Optional[ScreenStatus] = None,
        search: Optional[str] = None
    ) -> List[Screen]:
        """
        Get all screens with optional filtering.
        
        Args:
            db: Database session
            skip: Number of records to skip
            limit: Maximum number of records to return
            status: Filter by status
            search: Search by name or device_id
            
        Returns:
            List of screens
        """
        query = select(Screen)
        
        if status:
            query = query.where(Screen.status == status)
        
        if search:
            query = query.where(
                (Screen.name.ilike(f"%{search}%")) | 
                (Screen.device_id.ilike(f"%{search}%"))
            )
        
        query = query.offset(skip).limit(limit).order_by(Screen.created_at.desc())
        
        result = await db.execute(query)
        return result.scalars().all()
    
    async def get_by_id(self, db: AsyncSession, screen_id: str) -> Optional[Screen]:
        """
        Get screen by ID.
        
        Args:
            db: Database session
            screen_id: Screen UUID
            
        Returns:
            Screen or None
        """
        query = select(Screen).where(Screen.id == screen_id)
        result = await db.execute(query)
        return result.scalar_one_or_none()
    
    async def get_by_device_id(self, db: AsyncSession, device_id: str) -> Optional[Screen]:
        """
        Get screen by device ID.
        
        Args:
            db: Database session
            device_id: Device identifier
            
        Returns:
            Screen or None
        """
        query = select(Screen).where(Screen.device_id == device_id)
        result = await db.execute(query)
        return result.scalar_one_or_none()
    
    async def create(
        self,
        db: AsyncSession,
        name: str,
        device_id: str,
        location: Optional[str] = None,
        resolution: Optional[str] = None,
        api_key: Optional[str] = None
    ) -> Screen:
        """
        Create a new screen.
        
        Args:
            db: Database session
            name: Screen name
            device_id: Unique device identifier
            location: Physical location
            resolution: Screen resolution
            api_key: API key for device authentication
            
        Returns:
            Created screen
        """
        # Generate API key if not provided
        if not api_key:
            api_key = f"screen_{uuid.uuid4().hex}"
        
        screen = Screen(
            name=name,
            device_id=device_id,
            location=location,
            resolution=resolution,
            status=ScreenStatus.OFFLINE,
            api_key=api_key
        )
        
        db.add(screen)
        await db.commit()
        await db.refresh(screen)
        
        return screen
    
    async def update(
        self,
        db: AsyncSession,
        screen_id: str,
        name: Optional[str] = None,
        location: Optional[str] = None,
        resolution: Optional[str] = None,
        status: Optional[ScreenStatus] = None
    ) -> Optional[Screen]:
        """
        Update screen.
        
        Args:
            db: Database session
            screen_id: Screen UUID
            name: New name
            location: New location
            resolution: New resolution
            status: New status
            
        Returns:
            Updated screen or None
        """
        screen = await self.get_by_id(db, screen_id)
        
        if not screen:
            return None
        
        if name is not None:
            screen.name = name
        if location is not None:
            screen.location = location
        if resolution is not None:
            screen.resolution = resolution
        if status is not None:
            screen.status = status
        
        await db.commit()
        await db.refresh(screen)
        
        return screen
    
    async def delete(self, db: AsyncSession, screen_id: str) -> bool:
        """
        Delete screen.
        
        Args:
            db: Database session
            screen_id: Screen UUID
            
        Returns:
            True if deleted, False if not found
        """
        screen = await self.get_by_id(db, screen_id)
        
        if not screen:
            return False
        
        await db.delete(screen)
        await db.commit()
        
        return True
    
    async def update_heartbeat(
        self,
        db: AsyncSession,
        screen_id: str,
        status: ScreenStatus
    ) -> Optional[Screen]:
        """
        Update screen heartbeat.
        
        Args:
            db: Database session
            screen_id: Screen UUID
            status: New status (online/offline)
            
        Returns:
            Updated screen or None
        """
        screen = await self.get_by_id(db, screen_id)
        
        if not screen:
            return None
        
        screen.status = status
        screen.last_heartbeat = datetime.utcnow()
        
        await db.commit()
        await db.refresh(screen)
        
        return screen


class ScreenGroupService:
    """Service class for ScreenGroup operations."""
    
    async def get_all(
        self,
        db: AsyncSession,
        skip: int = 0,
        limit: int = 100
    ) -> List[ScreenGroup]:
        """
        Get all screen groups.
        
        Args:
            db: Database session
            skip: Number of records to skip
            limit: Maximum number of records to return
            
        Returns:
            List of screen groups
        """
        query = (
            select(ScreenGroup)
            .options(selectinload(ScreenGroup.screens))
            .offset(skip)
            .limit(limit)
            .order_by(ScreenGroup.created_at.desc())
        )
        
        result = await db.execute(query)
        return result.scalars().unique().all()
    
    async def get_by_id(self, db: AsyncSession, group_id: str) -> Optional[ScreenGroup]:
        """
        Get screen group by ID.
        
        Args:
            db: Database session
            group_id: Group UUID
            
        Returns:
            ScreenGroup or None
        """
        query = (
            select(ScreenGroup)
            .options(selectinload(ScreenGroup.screens))
            .where(ScreenGroup.id == group_id)
        )
        
        result = await db.execute(query)
        return result.scalar_one_or_none()
    
    async def create(
        self,
        db: AsyncSession,
        name: str,
        screen_ids: List[str] = None
    ) -> ScreenGroup:
        """
        Create a new screen group.
        
        Args:
            db: Database session
            name: Group name
            screen_ids: List of screen IDs to add to group
            
        Returns:
            Created screen group
        """
        group = ScreenGroup(name=name)
        
        db.add(group)
        await db.flush()  # Get the group ID
        
        # Add screen associations
        if screen_ids:
            for screen_id in screen_ids:
                # Verify screen exists
                screen_query = select(Screen).where(Screen.id == screen_id)
                screen_result = await db.execute(screen_query)
                if screen_result.scalar_one_or_none():
                    item = ScreenGroupItem(group_id=group.id, screen_id=screen_id)
                    db.add(item)
        
        await db.commit()
        await db.refresh(group)
        
        # Reload with screens
        return await self.get_by_id(db, group.id)
    
    async def delete(self, db: AsyncSession, group_id: str) -> bool:
        """
        Delete screen group.
        
        Args:
            db: Database session
            group_id: Group UUID
            
        Returns:
            True if deleted, False if not found
        """
        group = await self.get_by_id(db, group_id)
        
        if not group:
            return False
        
        await db.delete(group)
        await db.commit()
        
        return True
