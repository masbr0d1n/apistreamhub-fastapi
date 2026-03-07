"""
Campaign API routes - Videotron campaign management.
"""
from typing import Optional
from fastapi import APIRouter, Depends, status, Query, HTTPException
from sqlalchemy.ext.asyncio import AsyncSession

from app.db.base import get_db
from app.schemas.campaign import (
    CampaignCreate,
    CampaignUpdate,
    CampaignResponse,
    CampaignListResponse,
    CampaignDetailResponse,
    CampaignDeleteResponse,
    CampaignActivateResponse,
    CampaignDeactivateResponse,
)
from app.services.campaign_service import CampaignService


router = APIRouter(prefix="/campaigns", tags=["campaigns"])
campaign_service = CampaignService()


@router.get(
    "/",
    response_model=CampaignListResponse,
    summary="List all campaigns",
    description="Get all campaigns with optional filtering and pagination"
)
async def list_campaigns(
    skip: int = Query(0, ge=0, description="Number of records to skip"),
    limit: int = Query(100, ge=1, le=100, description="Maximum number of records to return"),
    db: AsyncSession = Depends(get_db)
) -> CampaignListResponse:
    """
    Get all campaigns.

    Args:
        skip: Number of records to skip
        limit: Maximum number of records to return
        db: Database session

    Returns:
        List of campaigns
    """
    campaigns = await campaign_service.get_all(db, skip, limit)
    
    return CampaignListResponse(
        campaigns=campaigns,
        count=len(campaigns)
    )


@router.get(
    "/{campaign_id}",
    response_model=CampaignDetailResponse,
    summary="Get campaign detail",
    description="Get detailed information about a specific campaign"
)
async def get_campaign(
    campaign_id: str,
    db: AsyncSession = Depends(get_db)
) -> CampaignDetailResponse:
    """
    Get campaign by ID.

    Args:
        campaign_id: Campaign UUID
        db: Database session

    Returns:
        Campaign details

    Raises:
        HTTPException: 404 if campaign not found
    """
    campaign = await campaign_service.get_by_id(db, campaign_id)
    
    if not campaign:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Campaign not found"
        )
    
    return CampaignDetailResponse(campaign=campaign)


@router.post(
    "/",
    response_model=CampaignDetailResponse,
    status_code=status.HTTP_201_CREATED,
    summary="Create campaign",
    description="Create a new campaign"
)
async def create_campaign(
    campaign_data: CampaignCreate,
    db: AsyncSession = Depends(get_db)
) -> CampaignDetailResponse:
    """
    Create a new campaign.

    Args:
        campaign_data: Campaign creation data
        db: Database session

    Returns:
        Created campaign
    """
    campaign = await campaign_service.create(
        db=db,
        name=campaign_data.name,
        description=campaign_data.description,
        screen_ids=campaign_data.screen_ids,
        layout_ids=campaign_data.layout_ids,
        start_date=campaign_data.start_date,
        end_date=campaign_data.end_date
    )
    
    return CampaignDetailResponse(campaign=campaign)


@router.put(
    "/{campaign_id}",
    response_model=CampaignDetailResponse,
    summary="Update campaign",
    description="Update campaign information"
)
async def update_campaign(
    campaign_id: str,
    campaign_data: CampaignUpdate,
    db: AsyncSession = Depends(get_db)
) -> CampaignDetailResponse:
    """
    Update campaign.

    Args:
        campaign_id: Campaign UUID
        campaign_data: Campaign update data
        db: Database session

    Returns:
        Updated campaign

    Raises:
        HTTPException: 404 if campaign not found
    """
    campaign = await campaign_service.update(
        db=db,
        campaign_id=campaign_id,
        name=campaign_data.name,
        description=campaign_data.description,
        screen_ids=campaign_data.screen_ids,
        layout_ids=campaign_data.layout_ids,
        start_date=campaign_data.start_date,
        end_date=campaign_data.end_date,
        status=campaign_data.status
    )
    
    if not campaign:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Campaign not found"
        )
    
    return CampaignDetailResponse(campaign=campaign)


@router.delete(
    "/{campaign_id}",
    response_model=CampaignDeleteResponse,
    summary="Delete campaign",
    description="Delete a campaign"
)
async def delete_campaign(
    campaign_id: str,
    db: AsyncSession = Depends(get_db)
) -> CampaignDeleteResponse:
    """
    Delete campaign.

    Args:
        campaign_id: Campaign UUID
        db: Database session

    Returns:
        Success message

    Raises:
        HTTPException: 404 if campaign not found
    """
    success = await campaign_service.delete(db, campaign_id)
    
    if not success:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Campaign not found"
        )
    
    return CampaignDeleteResponse()


@router.post(
    "/{campaign_id}/activate",
    response_model=CampaignActivateResponse,
    summary="Activate campaign",
    description="Activate a campaign"
)
async def activate_campaign(
    campaign_id: str,
    db: AsyncSession = Depends(get_db)
) -> CampaignActivateResponse:
    """
    Activate a campaign.

    Args:
        campaign_id: Campaign UUID
        db: Database session

    Returns:
        Activated campaign

    Raises:
        HTTPException: 404 if campaign not found
    """
    campaign = await campaign_service.activate(db, campaign_id)
    
    if not campaign:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Campaign not found"
        )
    
    return CampaignActivateResponse(
        message="Campaign activated successfully",
        campaign=campaign
    )


@router.post(
    "/{campaign_id}/deactivate",
    response_model=CampaignDeactivateResponse,
    summary="Deactivate campaign",
    description="Deactivate a campaign"
)
async def deactivate_campaign(
    campaign_id: str,
    db: AsyncSession = Depends(get_db)
) -> CampaignDeactivateResponse:
    """
    Deactivate a campaign.

    Args:
        campaign_id: Campaign UUID
        db: Database session

    Returns:
        Deactivated campaign

    Raises:
        HTTPException: 404 if campaign not found
    """
    campaign = await campaign_service.deactivate(db, campaign_id)
    
    if not campaign:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Campaign not found"
        )
    
    return CampaignDeactivateResponse(
        message="Campaign deactivated successfully",
        campaign=campaign
    )
