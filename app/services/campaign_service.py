"""
Campaign service - business logic for Videotron campaign management.
"""
import uuid
from datetime import datetime
from typing import List, Optional
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select

from app.models.campaign import Campaign


class CampaignService:
    """Service class for Campaign operations."""
    
    async def get_all(
        self,
        db: AsyncSession,
        skip: int = 0,
        limit: int = 100
    ) -> List[Campaign]:
        """
        Get all campaigns with optional filtering.
        
        Args:
            db: Database session
            skip: Number of records to skip
            limit: Maximum number of records to return
            
        Returns:
            List of campaigns
        """
        query = select(Campaign).offset(skip).limit(limit).order_by(Campaign.created_at.desc())
        
        result = await db.execute(query)
        return result.scalars().all()
    
    async def get_by_id(self, db: AsyncSession, campaign_id: str) -> Optional[Campaign]:
        """
        Get campaign by ID.
        
        Args:
            db: Database session
            campaign_id: Campaign UUID
            
        Returns:
            Campaign or None
        """
        query = select(Campaign).where(Campaign.id == campaign_id)
        result = await db.execute(query)
        return result.scalar_one_or_none()
    
    async def create(
        self,
        db: AsyncSession,
        name: str,
        description: Optional[str] = None,
        screen_ids: Optional[List[uuid.UUID]] = None,
        layout_ids: Optional[List[uuid.UUID]] = None,
        start_date: Optional[datetime] = None,
        end_date: Optional[datetime] = None,
        created_by: Optional[int] = None
    ) -> Campaign:
        """
        Create a new campaign.
        
        Args:
            db: Database session
            name: Campaign name
            description: Campaign description
            screen_ids: Array of screen UUIDs
            layout_ids: Array of layout UUIDs
            start_date: Campaign start date
            end_date: Campaign end date
            created_by: User ID who created the campaign
            
        Returns:
            Created campaign
        """
        # Convert UUIDs to strings for JSONB storage
        screen_id_strings = [str(sid) for sid in screen_ids] if screen_ids else []
        layout_id_strings = [str(lid) for lid in layout_ids] if layout_ids else []
        
        campaign = Campaign(
            name=name,
            description=description,
            screen_ids=screen_id_strings,
            layout_ids=layout_id_strings,
            start_date=start_date,
            end_date=end_date,
            created_by=created_by,
            status="draft"
        )
        
        db.add(campaign)
        await db.commit()
        await db.refresh(campaign)
        
        return campaign
    
    async def update(
        self,
        db: AsyncSession,
        campaign_id: str,
        name: Optional[str] = None,
        description: Optional[str] = None,
        screen_ids: Optional[List[uuid.UUID]] = None,
        layout_ids: Optional[List[uuid.UUID]] = None,
        start_date: Optional[datetime] = None,
        end_date: Optional[datetime] = None,
        status: Optional[str] = None
    ) -> Optional[Campaign]:
        """
        Update campaign.
        
        Args:
            db: Database session
            campaign_id: Campaign UUID
            name: New name
            description: New description
            screen_ids: New array of screen UUIDs
            layout_ids: New array of layout UUIDs
            start_date: New start date
            end_date: New end date
            status: New status
            
        Returns:
            Updated campaign or None
        """
        campaign = await self.get_by_id(db, campaign_id)
        
        if not campaign:
            return None
        
        if name is not None:
            campaign.name = name
        if description is not None:
            campaign.description = description
        if screen_ids is not None:
            campaign.screen_ids = [str(sid) for sid in screen_ids]
        if layout_ids is not None:
            campaign.layout_ids = [str(lid) for lid in layout_ids]
        if start_date is not None:
            campaign.start_date = start_date
        if end_date is not None:
            campaign.end_date = end_date
        if status is not None:
            campaign.status = status  # Already a string
        
        await db.commit()
        await db.refresh(campaign)
        
        return campaign
    
    async def delete(self, db: AsyncSession, campaign_id: str) -> bool:
        """
        Delete campaign.
        
        Args:
            db: Database session
            campaign_id: Campaign UUID
            
        Returns:
            True if deleted, False if not found
        """
        campaign = await self.get_by_id(db, campaign_id)
        
        if not campaign:
            return False
        
        await db.delete(campaign)
        await db.commit()
        
        return True
    
    async def activate(self, db: AsyncSession, campaign_id: str) -> Optional[Campaign]:
        """
        Activate a campaign.
        
        Args:
            db: Database session
            campaign_id: Campaign UUID
            
        Returns:
            Activated campaign or None
        """
        campaign = await self.get_by_id(db, campaign_id)
        
        if not campaign:
            return None
        
        campaign.status = "active"
        await db.commit()
        await db.refresh(campaign)
        
        return campaign
    
    async def deactivate(self, db: AsyncSession, campaign_id: str) -> Optional[Campaign]:
        """
        Deactivate a campaign.
        
        Args:
            db: Database session
            campaign_id: Campaign UUID
            
        Returns:
            Deactivated campaign or None
        """
        campaign = await self.get_by_id(db, campaign_id)
        
        if not campaign:
            return None
        
        campaign.status = "paused"
        await db.commit()
        await db.refresh(campaign)
        
        return campaign
