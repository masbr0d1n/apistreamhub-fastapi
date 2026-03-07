"""
Template service - business logic for Videotron template management.
"""
import uuid
from datetime import datetime
from typing import List, Optional
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select

from app.models.template import Template


class TemplateService:
    """Service class for Template operations."""
    
    async def get_all(
        self,
        db: AsyncSession,
        skip: int = 0,
        limit: int = 100,
        created_by: Optional[int] = None,
        category: Optional[str] = None
    ) -> List[Template]:
        """
        Get all templates with optional filtering.
        
        Args:
            db: Database session
            skip: Number of records to skip
            limit: Maximum number of records to return
            created_by: Filter by creator user ID
            category: Filter by category
            
        Returns:
            List of templates
        """
        query = select(Template)
        
        if created_by:
            query = query.where(Template.created_by == created_by)
        
        if category:
            query = query.where(Template.category == category)
        
        query = query.offset(skip).limit(limit).order_by(Template.created_at.desc())
        
        result = await db.execute(query)
        return result.scalars().all()
    
    async def get_by_id(self, db: AsyncSession, template_id: str) -> Optional[Template]:
        """
        Get template by ID.
        
        Args:
            db: Database session
            template_id: Template UUID
            
        Returns:
            Template or None
        """
        query = select(Template).where(Template.id == template_id)
        result = await db.execute(query)
        return result.scalar_one_or_none()
    
    async def create(
        self,
        db: AsyncSession,
        name: str,
        description: Optional[str] = None,
        layout_id: Optional[uuid.UUID] = None,
        thumbnail: Optional[str] = None,
        category: Optional[str] = None,
        created_by: Optional[int] = None
    ) -> Template:
        """
        Create a new template.
        
        Args:
            db: Database session
            name: Template name
            description: Template description
            layout_id: Associated layout UUID
            thumbnail: Base64 encoded thumbnail or file path
            category: Template category
            created_by: User ID who created the template
            
        Returns:
            Created template
        """
        template = Template(
            name=name,
            description=description,
            layout_id=layout_id,
            thumbnail=thumbnail,
            category=category,
            created_by=created_by
        )
        
        db.add(template)
        await db.commit()
        await db.refresh(template)
        
        return template
    
    async def update(
        self,
        db: AsyncSession,
        template_id: str,
        name: Optional[str] = None,
        description: Optional[str] = None,
        layout_id: Optional[uuid.UUID] = None,
        thumbnail: Optional[str] = None,
        category: Optional[str] = None
    ) -> Optional[Template]:
        """
        Update template.
        
        Args:
            db: Database session
            template_id: Template UUID
            name: New name
            description: New description
            layout_id: New layout UUID
            thumbnail: New thumbnail
            category: New category
            
        Returns:
            Updated template or None
        """
        template = await self.get_by_id(db, template_id)
        
        if not template:
            return None
        
        if name is not None:
            template.name = name
        if description is not None:
            template.description = description
        if layout_id is not None:
            template.layout_id = layout_id
        if thumbnail is not None:
            template.thumbnail = thumbnail
        if category is not None:
            template.category = category
        
        await db.commit()
        await db.refresh(template)
        
        return template
    
    async def delete(self, db: AsyncSession, template_id: str) -> bool:
        """
        Delete template.
        
        Args:
            db: Database session
            template_id: Template UUID
            
        Returns:
            True if deleted, False if not found
        """
        template = await self.get_by_id(db, template_id)
        
        if not template:
            return False
        
        await db.delete(template)
        await db.commit()
        
        return True
    
    async def duplicate(
        self,
        db: AsyncSession,
        template_id: str,
        new_name: Optional[str] = None
    ) -> Optional[Template]:
        """
        Duplicate an existing template.
        
        Args:
            db: Database session
            template_id: Template UUID to duplicate
            new_name: New name for the duplicated template (optional)
            
        Returns:
            Duplicated template or None
        """
        original = await self.get_by_id(db, template_id)
        
        if not original:
            return None
        
        # Generate new name if not provided
        if not new_name:
            new_name = f"{original.name} (Copy)"
        
        # Create duplicate
        template = Template(
            name=new_name,
            description=original.description,
            layout_id=original.layout_id,
            thumbnail=original.thumbnail,
            category=original.category,
            created_by=original.created_by
        )
        
        db.add(template)
        await db.commit()
        await db.refresh(template)
        
        return template
