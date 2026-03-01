"""
Role Preset service - business logic for role preset operations
"""
from datetime import datetime
from sqlalchemy import select, delete
from sqlalchemy.ext.asyncio import AsyncSession

from app.models.role_preset import RolePreset
from app.schemas.role_preset import RolePresetCreate, RolePresetUpdate
from app.core.exceptions import NotFoundException, ConflictException, ForbiddenException


class RolePresetService:
    """Service for role preset operations."""
    
    async def get_all(self, db: AsyncSession, include_inactive: bool = False) -> list[RolePreset]:
        """
        Get all role presets.
        
        Args:
            db: Database session
            include_inactive: Whether to include inactive presets
            
        Returns:
            List of role presets
        """
        query = select(RolePreset)
        if not include_inactive:
            query = query.where(RolePreset.is_active == True)
        
        query = query.order_by(RolePreset.is_system.desc(), RolePreset.name.asc())
        
        result = await db.execute(query)
        return list(result.scalars().all())
    
    async def get_by_id(self, db: AsyncSession, preset_id: int) -> RolePreset:
        """
        Get role preset by ID.
        
        Args:
            db: Database session
            preset_id: Role preset ID
            
        Returns:
            Role preset
            
        Raises:
            NotFoundException: If preset not found
        """
        result = await db.execute(
            select(RolePreset).where(RolePreset.id == preset_id)
        )
        preset = result.scalar_one_or_none()
        
        if not preset:
            raise NotFoundException(f"Role preset with ID {preset_id} not found")
        
        return preset
    
    async def create(self, db: AsyncSession, preset_data: RolePresetCreate, created_by: int) -> RolePreset:
        """
        Create a new role preset.
        
        Args:
            db: Database session
            preset_data: Role preset data
            created_by: User ID who is creating this preset
            
        Returns:
            Created role preset
            
        Raises:
            ConflictException: If preset name already exists
        """
        # Check if name exists
        result = await db.execute(
            select(RolePreset).where(RolePreset.name == preset_data.name)
        )
        if result.scalar_one_or_none():
            raise ConflictException(f"Role preset '{preset_data.name}' already exists")
        
        preset = RolePreset(
            name=preset_data.name,
            description=preset_data.description,
            page_access=preset_data.page_access,
            created_by=created_by
        )
        
        db.add(preset)
        await db.commit()
        await db.refresh(preset)
        
        return preset
    
    async def update(self, db: AsyncSession, preset_id: int, preset_data: RolePresetUpdate) -> RolePreset:
        """
        Update role preset.
        
        Args:
            db: Database session
            preset_id: Role preset ID
            preset_data: Update data
            
        Returns:
            Updated role preset
            
        Raises:
            NotFoundException: If preset not found
            ForbiddenException: If trying to modify system preset
        """
        preset = await self.get_by_id(db, preset_id)
        
        # Cannot modify system presets
        if preset.is_system:
            raise ForbiddenException("Cannot modify system role preset")
        
        # Check name uniqueness if name is being changed
        if preset_data.name and preset_data.name != preset.name:
            result = await db.execute(
                select(RolePreset).where(RolePreset.name == preset_data.name)
            )
            if result.scalar_one_or_none():
                raise ConflictException(f"Role preset '{preset_data.name}' already exists")
        
        # Update fields
        if preset_data.name:
            preset.name = preset_data.name
        if preset_data.description is not None:
            preset.description = preset_data.description
        if preset_data.page_access is not None:
            preset.page_access = preset_data.page_access
        if preset_data.is_active is not None:
            preset.is_active = preset_data.is_active
        
        await db.commit()
        await db.refresh(preset)
        
        return preset
    
    async def delete(self, db: AsyncSession, preset_id: int) -> RolePreset:
        """
        Delete role preset.
        
        Args:
            db: Database session
            preset_id: Role preset ID
            
        Returns:
            Deleted role preset
            
        Raises:
            NotFoundException: If preset not found
            ForbiddenException: If trying to delete system preset
        """
        preset = await self.get_by_id(db, preset_id)
        
        # Cannot delete system presets
        if preset.is_system:
            raise ForbiddenException("Cannot delete system role preset")
        
        await db.execute(
            delete(RolePreset).where(RolePreset.id == preset_id)
        )
        await db.commit()
        
        return preset
