"""
Screen API routes - Videotron device management.
"""
from typing import Optional
from uuid import UUID
from fastapi import APIRouter, Depends, status, Query, HTTPException
from sqlalchemy.ext.asyncio import AsyncSession

from app.db.base import get_db
from app.schemas.screen import (
    ScreenCreate,
    ScreenUpdate,
    ScreenHeartbeat,
    ScreenResponse,
    ScreenListResponse,
    ScreenDetailResponse,
    ScreenDeleteResponse,
    ScreenHeartbeatResponse,
    ScreenGroupCreate,
    ScreenGroupResponse,
    ScreenGroupListResponse,
    ScreenGroupDetailResponse,
    ScreenGroupDeleteResponse,
    ScreenStatusEnum
)
from app.services.screen_service import ScreenService, ScreenGroupService
from app.models.screen import ScreenStatus
from app.core.security import get_current_user
from app.schemas.auth import UserResponse


router = APIRouter(prefix="/screens", tags=["screens"])
screen_service = ScreenService()
screen_group_service = ScreenGroupService()


# ============================================================================
# SCREEN GROUPS ENDPOINTS (Must be defined BEFORE /{screen_id} routes)
# ============================================================================

@router.get(
    "/groups",
    response_model=ScreenGroupListResponse,
    summary="List screen groups",
    description="Get all screen groups"
)
async def list_screen_groups(
    skip: int = Query(0, ge=0, description="Number of records to skip"),
    limit: int = Query(100, ge=1, le=100, description="Maximum number of records to return"),
    db: AsyncSession = Depends(get_db)
) -> ScreenGroupListResponse:
    """
    Get all screen groups.

    Args:
        skip: Number of records to skip
        limit: Maximum number of records to return
        db: Database session

    Returns:
        List of screen groups
    """
    groups = await screen_group_service.get_all(db, skip, limit)
    
    # Convert to response format with screen_ids
    group_responses = []
    for group in groups:
        group_responses.append(
            ScreenGroupResponse(
                id=group.id,
                name=group.name,
                screen_ids=[screen.id for screen in group.screens],
                created_at=group.created_at
            )
        )
    
    return ScreenGroupListResponse(
        groups=group_responses,
        count=len(group_responses)
    )


@router.post(
    "/groups",
    response_model=ScreenGroupDetailResponse,
    status_code=status.HTTP_201_CREATED,
    summary="Create screen group",
    description="Create a new screen group"
)
async def create_screen_group(
    group_data: ScreenGroupCreate,
    db: AsyncSession = Depends(get_db)
) -> ScreenGroupDetailResponse:
    """
    Create a new screen group.

    Args:
        group_data: Screen group creation data
        db: Database session

    Returns:
        Created screen group
    """
    group = await screen_group_service.create(
        db=db,
        name=group_data.name,
        screen_ids=group_data.screen_ids
    )
    
    # Convert to response format
    group_response = ScreenGroupResponse(
        id=group.id,
        name=group.name,
        screen_ids=[screen.id for screen in group.screens],
        created_at=group.created_at
    )
    
    return ScreenGroupDetailResponse(group=group_response)


@router.delete(
    "/groups/{group_id}",
    response_model=ScreenGroupDeleteResponse,
    summary="Delete screen group",
    description="Delete a screen group (admin only)"
)
async def delete_screen_group(
    group_id: UUID,
    db: AsyncSession = Depends(get_db),
    current_user: UserResponse = Depends(get_current_user)
) -> ScreenGroupDeleteResponse:
    """
    Delete a screen group.
    
    Requires admin role. Cascade deletes all screen_group_items.

    Args:
        group_id: Screen group UUID
        db: Database session
        current_user: Current authenticated user

    Returns:
        Success message

    Raises:
        HTTPException: 403 if not admin, 404 if group not found
    """
    # Check permissions
    if current_user.role not in ['admin', 'superadmin']:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Not enough permissions"
        )
    
    # Delete screen group (cascade deletes items)
    success = await screen_group_service.delete(db, str(group_id))
    
    if not success:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Screen group not found"
        )
    
    return ScreenGroupDeleteResponse()


# ============================================================================
# SCREEN ENDPOINTS
# ============================================================================

@router.get(
    "/",
    response_model=ScreenListResponse,
    summary="List all screens",
    description="Get all screens with optional filtering and pagination"
)
async def list_screens(
    skip: int = Query(0, ge=0, description="Number of records to skip"),
    limit: int = Query(100, ge=1, le=100, description="Maximum number of records to return"),
    status: Optional[ScreenStatusEnum] = Query(None, description="Filter by status"),
    search: Optional[str] = Query(None, description="Search by name or device_id"),
    db: AsyncSession = Depends(get_db)
) -> ScreenListResponse:
    """
    Get all screens.

    Args:
        skip: Number of records to skip
        limit: Maximum number of records to return
        status: Filter by status (online/offline/maintenance)
        search: Search by name or device_id
        db: Database session

    Returns:
        List of screens
    """
    # Convert ScreenStatusEnum to ScreenStatus if provided
    screen_status = None
    if status:
        screen_status = ScreenStatus(status.value)
    
    screens = await screen_service.get_all(
        db, skip, limit, screen_status, search
    )
    
    return ScreenListResponse(
        screens=screens,
        count=len(screens)
    )


@router.get(
    "/{screen_id}",
    response_model=ScreenDetailResponse,
    summary="Get screen detail",
    description="Get detailed information about a specific screen"
)
async def get_screen(
    screen_id: str,
    db: AsyncSession = Depends(get_db)
) -> ScreenDetailResponse:
    """
    Get screen by ID.

    Args:
        screen_id: Screen UUID
        db: Database session

    Returns:
        Screen details

    Raises:
        HTTPException: 404 if screen not found
    """
    screen = await screen_service.get_by_id(db, screen_id)
    
    if not screen:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Screen not found"
        )
    
    return ScreenDetailResponse(screen=screen)


@router.post(
    "/",
    response_model=ScreenDetailResponse,
    status_code=status.HTTP_201_CREATED,
    summary="Create screen",
    description="Create a new screen device"
)
async def create_screen(
    screen_data: ScreenCreate,
    db: AsyncSession = Depends(get_db)
) -> ScreenDetailResponse:
    """
    Create a new screen.

    Args:
        screen_data: Screen creation data
        db: Database session

    Returns:
        Created screen

    Raises:
        HTTPException: 400 if device_id already exists
    """
    # Check if device_id already exists
    existing = await screen_service.get_by_device_id(db, screen_data.device_id)
    if existing:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Device ID already exists"
        )
    
    screen = await screen_service.create(
        db=db,
        name=screen_data.name,
        device_id=screen_data.device_id,
        location=screen_data.location,
        resolution=screen_data.resolution
    )
    
    return ScreenDetailResponse(screen=screen)


@router.put(
    "/{screen_id}",
    response_model=ScreenDetailResponse,
    summary="Update screen",
    description="Update screen information"
)
async def update_screen(
    screen_id: str,
    screen_data: ScreenUpdate,
    db: AsyncSession = Depends(get_db)
) -> ScreenDetailResponse:
    """
    Update screen.

    Args:
        screen_id: Screen UUID
        screen_data: Screen update data
        db: Database session

    Returns:
        Updated screen

    Raises:
        HTTPException: 404 if screen not found
    """
    # Convert ScreenStatusEnum to ScreenStatus if provided
    screen_status = None
    if screen_data.status:
        screen_status = ScreenStatus(screen_data.status.value)
    
    screen = await screen_service.update(
        db=db,
        screen_id=screen_id,
        name=screen_data.name,
        location=screen_data.location,
        resolution=screen_data.resolution,
        status=screen_status
    )
    
    if not screen:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Screen not found"
        )
    
    return ScreenDetailResponse(screen=screen)


@router.delete(
    "/{screen_id}",
    response_model=ScreenDeleteResponse,
    summary="Delete screen",
    description="Delete a screen device"
)
async def delete_screen(
    screen_id: str,
    db: AsyncSession = Depends(get_db)
) -> ScreenDeleteResponse:
    """
    Delete screen.

    Args:
        screen_id: Screen UUID
        db: Database session

    Returns:
        Success message

    Raises:
        HTTPException: 404 if screen not found
    """
    success = await screen_service.delete(db, screen_id)
    
    if not success:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Screen not found"
        )
    
    return ScreenDeleteResponse()


@router.post(
    "/{screen_id}/heartbeat",
    response_model=ScreenHeartbeatResponse,
    summary="Update screen heartbeat",
    description="Update screen heartbeat and status"
)
async def update_heartbeat(
    screen_id: str,
    heartbeat_data: ScreenHeartbeat,
    db: AsyncSession = Depends(get_db)
) -> ScreenHeartbeatResponse:
    """
    Update screen heartbeat.

    Args:
        screen_id: Screen UUID
        heartbeat_data: Heartbeat data with status
        db: Database session

    Returns:
        Heartbeat response with timestamp

    Raises:
        HTTPException: 404 if screen not found
    """
    # Convert ScreenStatusEnum to ScreenStatus
    status = ScreenStatus(heartbeat_data.status.value)
    
    screen = await screen_service.update_heartbeat(db, screen_id, status)
    
    if not screen:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Screen not found"
        )
    
    return ScreenHeartbeatResponse(
        last_heartbeat=screen.last_heartbeat
    )
