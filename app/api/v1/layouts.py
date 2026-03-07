"""
Layout API routes - Videotron layout management.
"""
from typing import Optional
from fastapi import APIRouter, Depends, status, Query, HTTPException
from sqlalchemy.ext.asyncio import AsyncSession

from app.db.base import get_db
from app.schemas.layout import (
    LayoutCreate,
    LayoutUpdate,
    LayoutResponse,
    LayoutListResponse,
    LayoutDetailResponse,
    LayoutDeleteResponse,
    LayoutDuplicateRequest,
)
from app.services.layout_service import LayoutService


router = APIRouter(prefix="/layouts", tags=["layouts"])
layout_service = LayoutService()


@router.get(
    "/",
    response_model=LayoutListResponse,
    summary="List all layouts",
    description="Get all layouts with optional filtering and pagination"
)
async def list_layouts(
    skip: int = Query(0, ge=0, description="Number of records to skip"),
    limit: int = Query(100, ge=1, le=100, description="Maximum number of records to return"),
    created_by: Optional[int] = Query(None, description="Filter by creator user ID"),
    db: AsyncSession = Depends(get_db)
) -> LayoutListResponse:
    """
    Get all layouts.

    Args:
        skip: Number of records to skip
        limit: Maximum number of records to return
        created_by: Filter by creator user ID
        db: Database session

    Returns:
        List of layouts
    """
    layouts = await layout_service.get_all(db, skip, limit, created_by)
    
    return LayoutListResponse(
        layouts=layouts,
        count=len(layouts)
    )


@router.get(
    "/{layout_id}",
    response_model=LayoutDetailResponse,
    summary="Get layout detail",
    description="Get detailed information about a specific layout"
)
async def get_layout(
    layout_id: str,
    db: AsyncSession = Depends(get_db)
) -> LayoutDetailResponse:
    """
    Get layout by ID.

    Args:
        layout_id: Layout UUID
        db: Database session

    Returns:
        Layout details

    Raises:
        HTTPException: 404 if layout not found
    """
    layout = await layout_service.get_by_id(db, layout_id)
    
    if not layout:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Layout not found"
        )
    
    return LayoutDetailResponse(layout=layout)


@router.post(
    "/",
    response_model=LayoutDetailResponse,
    status_code=status.HTTP_201_CREATED,
    summary="Create layout",
    description="Create a new layout"
)
async def create_layout(
    layout_data: LayoutCreate,
    db: AsyncSession = Depends(get_db)
) -> LayoutDetailResponse:
    """
    Create a new layout.

    Args:
        layout_data: Layout creation data
        db: Database session

    Returns:
        Created layout
    """
    layout = await layout_service.create(
        db=db,
        name=layout_data.name,
        canvas_config=layout_data.canvas_config,
        layers=layout_data.layers
    )
    
    return LayoutDetailResponse(layout=layout)


@router.put(
    "/{layout_id}",
    response_model=LayoutDetailResponse,
    summary="Update layout",
    description="Update layout information"
)
async def update_layout(
    layout_id: str,
    layout_data: LayoutUpdate,
    db: AsyncSession = Depends(get_db)
) -> LayoutDetailResponse:
    """
    Update layout.

    Args:
        layout_id: Layout UUID
        layout_data: Layout update data
        db: Database session

    Returns:
        Updated layout

    Raises:
        HTTPException: 404 if layout not found
    """
    layout = await layout_service.update(
        db=db,
        layout_id=layout_id,
        name=layout_data.name,
        canvas_config=layout_data.canvas_config,
        layers=layout_data.layers
    )
    
    if not layout:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Layout not found"
        )
    
    return LayoutDetailResponse(layout=layout)


@router.delete(
    "/{layout_id}",
    response_model=LayoutDeleteResponse,
    summary="Delete layout",
    description="Delete a layout"
)
async def delete_layout(
    layout_id: str,
    db: AsyncSession = Depends(get_db)
) -> LayoutDeleteResponse:
    """
    Delete layout.

    Args:
        layout_id: Layout UUID
        db: Database session

    Returns:
        Success message

    Raises:
        HTTPException: 404 if layout not found
    """
    success = await layout_service.delete(db, layout_id)
    
    if not success:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Layout not found"
        )
    
    return LayoutDeleteResponse()


@router.post(
    "/{layout_id}/duplicate",
    response_model=LayoutDetailResponse,
    status_code=status.HTTP_201_CREATED,
    summary="Duplicate layout",
    description="Duplicate an existing layout"
)
async def duplicate_layout(
    layout_id: str,
    duplicate_data: Optional[LayoutDuplicateRequest] = None,
    db: AsyncSession = Depends(get_db)
) -> LayoutDetailResponse:
    """
    Duplicate an existing layout.

    Args:
        layout_id: Layout UUID to duplicate
        duplicate_data: Optional new name for the duplicated layout
        db: Database session

    Returns:
        Duplicated layout

    Raises:
        HTTPException: 404 if layout not found
    """
    new_name = duplicate_data.name if duplicate_data else None
    
    layout = await layout_service.duplicate(db, layout_id, new_name)
    
    if not layout:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Layout not found"
        )
    
    return LayoutDetailResponse(layout=layout)
