"""
Layout service - business logic for Videotron layout management.
"""
import uuid
from datetime import datetime
from typing import List, Optional
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select

from app.models.layout import Layout


class LayoutService:
    """Service class for Layout operations."""
    
    async def get_all(
        self,
        db: AsyncSession,
        skip: int = 0,
        limit: int = 100,
        created_by: Optional[int] = None
    ) -> List[Layout]:
        """
        Get all layouts with optional filtering.
        
        Args:
            db: Database session
            skip: Number of records to skip
            limit: Maximum number of records to return
            created_by: Filter by creator user ID
            
        Returns:
            List of layouts
        """
        query = select(Layout)
        
        if created_by:
            query = query.where(Layout.created_by == created_by)
        
        query = query.offset(skip).limit(limit).order_by(Layout.created_at.desc())
        
        result = await db.execute(query)
        return result.scalars().all()
    
    async def get_by_id(self, db: AsyncSession, layout_id: str) -> Optional[Layout]:
        """
        Get layout by ID.
        
        Args:
            db: Database session
            layout_id: Layout UUID
            
        Returns:
            Layout or None
        """
        query = select(Layout).where(Layout.id == layout_id)
        result = await db.execute(query)
        return result.scalar_one_or_none()
    
    async def create(
        self,
        db: AsyncSession,
        name: str,
        canvas_config: Optional[dict] = None,
        layers: Optional[List[dict]] = None,
        created_by: Optional[int] = None
    ) -> Layout:
        """
        Create a new layout.
        
        Args:
            db: Database session
            name: Layout name
            canvas_config: Canvas configuration
            layers: Array of layer objects
            created_by: User ID who created the layout
            
        Returns:
            Created layout
        """
        layout = Layout(
            name=name,
            canvas_config=canvas_config,
            layers=layers or [],
            created_by=created_by
        )
        
        db.add(layout)
        await db.commit()
        await db.refresh(layout)
        
        return layout
    
    async def update(
        self,
        db: AsyncSession,
        layout_id: str,
        name: Optional[str] = None,
        canvas_config: Optional[dict] = None,
        layers: Optional[List[dict]] = None
    ) -> Optional[Layout]:
        """
        Update layout.
        
        Args:
            db: Database session
            layout_id: Layout UUID
            name: New name
            canvas_config: New canvas configuration
            layers: New array of layer objects
            
        Returns:
            Updated layout or None
        """
        layout = await self.get_by_id(db, layout_id)
        
        if not layout:
            return None
        
        if name is not None:
            layout.name = name
        if canvas_config is not None:
            layout.canvas_config = canvas_config
        if layers is not None:
            layout.layers = layers
        
        await db.commit()
        await db.refresh(layout)
        
        return layout
    
    async def delete(self, db: AsyncSession, layout_id: str) -> bool:
        """
        Delete layout.
        
        Args:
            db: Database session
            layout_id: Layout UUID
            
        Returns:
            True if deleted, False if not found
        """
        layout = await self.get_by_id(db, layout_id)
        
        if not layout:
            return False
        
        await db.delete(layout)
        await db.commit()
        
        return True
    
    async def duplicate(
        self,
        db: AsyncSession,
        layout_id: str,
        new_name: Optional[str] = None
    ) -> Optional[Layout]:
        """
        Duplicate an existing layout.
        
        Args:
            db: Database session
            layout_id: Layout UUID to duplicate
            new_name: New name for the duplicated layout (optional)
            
        Returns:
            Duplicated layout or None
        """
        original = await self.get_by_id(db, layout_id)
        
        if not original:
            return None
        
        # Generate new name if not provided
        if not new_name:
            new_name = f"{original.name} (Copy)"
        
        # Create duplicate with deep copy of canvas_config and layers
        import copy
        layout = Layout(
            name=new_name,
            canvas_config=copy.deepcopy(original.canvas_config) if original.canvas_config else None,
            layers=copy.deepcopy(original.layers) if original.layers else [],
            created_by=original.created_by
        )
        
        db.add(layout)
        await db.commit()
        await db.refresh(layout)
        
        return layout
