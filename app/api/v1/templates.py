"""
Template API routes - Videotron template management.
"""
from typing import Optional
from fastapi import APIRouter, Depends, status, Query, HTTPException
from sqlalchemy.ext.asyncio import AsyncSession

from app.db.base import get_db
from app.schemas.template import (
    TemplateCreate,
    TemplateUpdate,
    TemplateResponse,
    TemplateListResponse,
    TemplateDetailResponse,
    TemplateDeleteResponse,
    TemplateDuplicateRequest,
)
from app.services.template_service import TemplateService


router = APIRouter(prefix="/templates", tags=["templates"])
template_service = TemplateService()


@router.get(
    "/",
    response_model=TemplateListResponse,
    summary="List all templates",
    description="Get all templates with optional filtering and pagination"
)
async def list_templates(
    skip: int = Query(0, ge=0, description="Number of records to skip"),
    limit: int = Query(100, ge=1, le=100, description="Maximum number of records to return"),
    created_by: Optional[int] = Query(None, description="Filter by creator user ID"),
    category: Optional[str] = Query(None, description="Filter by category"),
    db: AsyncSession = Depends(get_db)
) -> TemplateListResponse:
    """
    Get all templates.

    Args:
        skip: Number of records to skip
        limit: Maximum number of records to return
        created_by: Filter by creator user ID
        category: Filter by category
        db: Database session

    Returns:
        List of templates
    """
    templates = await template_service.get_all(db, skip, limit, created_by, category)
    
    return TemplateListResponse(
        templates=templates,
        count=len(templates)
    )


@router.get(
    "/{template_id}",
    response_model=TemplateDetailResponse,
    summary="Get template detail",
    description="Get detailed information about a specific template"
)
async def get_template(
    template_id: str,
    db: AsyncSession = Depends(get_db)
) -> TemplateDetailResponse:
    """
    Get template by ID.

    Args:
        template_id: Template UUID
        db: Database session

    Returns:
        Template details

    Raises:
        HTTPException: 404 if template not found
    """
    template = await template_service.get_by_id(db, template_id)
    
    if not template:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Template not found"
        )
    
    return TemplateDetailResponse(template=template)


@router.post(
    "/",
    response_model=TemplateDetailResponse,
    status_code=status.HTTP_201_CREATED,
    summary="Create template",
    description="Create a new template"
)
async def create_template(
    template_data: TemplateCreate,
    db: AsyncSession = Depends(get_db)
) -> TemplateDetailResponse:
    """
    Create a new template.

    Args:
        template_data: Template creation data
        db: Database session

    Returns:
        Created template
    """
    template = await template_service.create(
        db=db,
        name=template_data.name,
        description=template_data.description,
        layout_id=template_data.layout_id,
        thumbnail=template_data.thumbnail,
        category=template_data.category
    )
    
    return TemplateDetailResponse(template=template)


@router.put(
    "/{template_id}",
    response_model=TemplateDetailResponse,
    summary="Update template",
    description="Update template information"
)
async def update_template(
    template_id: str,
    template_data: TemplateUpdate,
    db: AsyncSession = Depends(get_db)
) -> TemplateDetailResponse:
    """
    Update template.

    Args:
        template_id: Template UUID
        template_data: Template update data
        db: Database session

    Returns:
        Updated template

    Raises:
        HTTPException: 404 if template not found
    """
    template = await template_service.update(
        db=db,
        template_id=template_id,
        name=template_data.name,
        description=template_data.description,
        layout_id=template_data.layout_id,
        thumbnail=template_data.thumbnail,
        category=template_data.category
    )
    
    if not template:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Template not found"
        )
    
    return TemplateDetailResponse(template=template)


@router.delete(
    "/{template_id}",
    response_model=TemplateDeleteResponse,
    summary="Delete template",
    description="Delete a template"
)
async def delete_template(
    template_id: str,
    db: AsyncSession = Depends(get_db)
) -> TemplateDeleteResponse:
    """
    Delete template.

    Args:
        template_id: Template UUID
        db: Database session

    Returns:
        Success message

    Raises:
        HTTPException: 404 if template not found
    """
    success = await template_service.delete(db, template_id)
    
    if not success:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Template not found"
        )
    
    return TemplateDeleteResponse()


@router.post(
    "/{template_id}/duplicate",
    response_model=TemplateDetailResponse,
    status_code=status.HTTP_201_CREATED,
    summary="Duplicate template",
    description="Duplicate an existing template"
)
async def duplicate_template(
    template_id: str,
    duplicate_data: Optional[TemplateDuplicateRequest] = None,
    db: AsyncSession = Depends(get_db)
) -> TemplateDetailResponse:
    """
    Duplicate an existing template.

    Args:
        template_id: Template UUID to duplicate
        duplicate_data: Optional new name for the duplicated template
        db: Database session

    Returns:
        Duplicated template

    Raises:
        HTTPException: 404 if template not found
    """
    new_name = duplicate_data.name if duplicate_data else None
    
    template = await template_service.duplicate(db, template_id, new_name)
    
    if not template:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Template not found"
        )
    
    return TemplateDetailResponse(template=template)
