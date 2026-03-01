"""
Role Preset API endpoints - CRUD operations for role presets
"""
from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.ext.asyncio import AsyncSession

from app.db.base import get_db
from app.schemas.role_preset import (
    RolePresetCreate, 
    RolePresetUpdate, 
    RolePresetListResponse,
    RolePresetResponse
)
from app.services.role_preset_service import RolePresetService
from app.services.auth_service import AuthService
from app.api.v1.auth import get_current_user
from app.models.user import User, UserRole

router = APIRouter()


@router.get("/", response_model=RolePresetListResponse)
async def get_all_role_presets(
    include_inactive: bool = False,
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    """
    Get all role presets.
    
    Requires: User role (any authenticated user)
    """
    service = RolePresetService()
    presets = await service.get_all(db, include_inactive=include_inactive)
    
    return RolePresetListResponse(
        status=True,
        statusCode=200,
        message="Role presets retrieved successfully",
        data=[
            RolePresetResponse(
                id=p.id,
                name=p.name,
                description=p.description,
                page_access=p.page_access,
                is_system=p.is_system,
                is_active=p.is_active,
                created_at=p.created_at.isoformat()
            )
            for p in presets
        ]
    )


@router.post("/", response_model=dict, status_code=status.HTTP_201_CREATED)
async def create_role_preset(
    preset_data: RolePresetCreate,
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    """
    Create a new role preset.
    
    Requires: ADMIN or SUPERADMIN role
    """
    # Check permissions
    if current_user.role not in [UserRole.ADMIN, UserRole.SUPERADMIN]:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Only admins can create role presets"
        )
    
    service = RolePresetService()
    preset = await service.create(db, preset_data, created_by=current_user.id)
    
    return {
        "status": True,
        "statusCode": 201,
        "message": "Role preset created successfully",
        "data": {
            "id": preset.id,
            "name": preset.name,
            "description": preset.description,
            "page_access": preset.page_access,
            "is_system": preset.is_system,
            "is_active": preset.is_active,
            "created_at": preset.created_at.isoformat()
        }
    }


@router.get("/{preset_id}", response_model=dict)
async def get_role_preset(
    preset_id: int,
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    """Get role preset by ID."""
    service = RolePresetService()
    preset = await service.get_by_id(db, preset_id)
    
    return {
        "status": True,
        "statusCode": 200,
        "message": "Role preset retrieved successfully",
        "data": {
            "id": preset.id,
            "name": preset.name,
            "description": preset.description,
            "page_access": preset.page_access,
            "is_system": preset.is_system,
            "is_active": preset.is_active,
            "created_at": preset.created_at.isoformat()
        }
    }


@router.post("", response_model=dict, status_code=status.HTTP_201_CREATED)
async def create_role_preset(
    preset_data: RolePresetCreate,
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    """
    Create a new role preset.
    
    Requires: ADMIN or SUPERADMIN role
    """
    # Check permissions
    if current_user.role not in [UserRole.ADMIN, UserRole.SUPERADMIN]:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Only admins can create role presets"
        )
    
    service = RolePresetService()
    preset = await service.create(db, preset_data, created_by=current_user.id)
    
    return {
        "status": True,
        "statusCode": 201,
        "message": "Role preset created successfully",
        "data": {
            "id": preset.id,
            "name": preset.name,
            "description": preset.description,
            "page_access": preset.page_access,
            "is_system": preset.is_system,
            "is_active": preset.is_active,
            "created_at": preset.created_at.isoformat()
        }
    }


@router.put("/{preset_id}", response_model=dict)
async def update_role_preset(
    preset_id: int,
    preset_data: RolePresetUpdate,
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    """
    Update role preset.
    
    Requires: SUPERADMIN role
    """
    # Check permissions - only superadmin can modify presets
    if current_user.role != UserRole.SUPERADMIN:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Only superadmin can modify role presets"
        )
    
    service = RolePresetService()
    preset = await service.update(db, preset_id, preset_data)
    
    return {
        "status": True,
        "statusCode": 200,
        "message": "Role preset updated successfully",
        "data": {
            "id": preset.id,
            "name": preset.name,
            "description": preset.description,
            "page_access": preset.page_access,
            "is_system": preset.is_system,
            "is_active": preset.is_active,
            "created_at": preset.created_at.isoformat()
        }
    }


@router.delete("/{preset_id}", response_model=dict)
async def delete_role_preset(
    preset_id: int,
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    """
    Delete role preset.
    
    Requires: SUPERADMIN role
    """
    # Check permissions
    if current_user.role != UserRole.SUPERADMIN:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Only superadmin can delete role presets"
        )
    
    service = RolePresetService()
    preset = await service.delete(db, preset_id)
    
    return {
        "status": True,
        "statusCode": 200,
        "message": "Role preset deleted successfully",
        "data": {
            "id": preset.id,
            "name": preset.name
        }
    }
