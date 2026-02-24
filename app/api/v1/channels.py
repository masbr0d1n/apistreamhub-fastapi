"""
Channel API routes.
"""
from typing import List
from fastapi import APIRouter, Depends, status
from sqlalchemy.ext.asyncio import AsyncSession

from app.db.base import get_db
from app.schemas.channel import (
    ChannelCreate,
    ChannelUpdate,
    ChannelResponse,
    ChannelListResponse,
    ChannelDetailResponse
)
from app.services.channel_service import ChannelService
from app.core.exceptions import StreamHubException


router = APIRouter(prefix="/channels", tags=["channels"])
channel_service = ChannelService()


@router.get(
    "/list",
    response_model=ChannelListResponse,
    summary="List all channels",
    description="Get all channels with pagination"
)
async def list_channels(
    skip: int = 0,
    limit: int = 100,
    db: AsyncSession = Depends(get_db)
) -> ChannelListResponse:
    """
    Get all channels.
    
    Args:
        skip: Number of records to skip
        limit: Maximum number of records to return
        db: Database session
        
    Returns:
        List of channels
    """
    try:
        channels = await channel_service.get_all(db, skip, limit)
        
        return ChannelListResponse(
            status=True,
            statusCode=200,
            message="Success",
            data=[ChannelResponse.model_validate(c) for c in channels],
            count=len(channels)
        )
    except StreamHubException as e:
        raise e
    except Exception as e:
        raise StreamHubException(str(e))


@router.get(
    "/",
    response_model=ChannelListResponse,
    summary="List all channels (alternative endpoint)",
    description="Get all channels - same as /list"
)
async def get_all_channels(
    skip: int = 0,
    limit: int = 100,
    db: AsyncSession = Depends(get_db)
) -> ChannelListResponse:
    """Get all channels (alternative endpoint)."""
    return await list_channels(skip, limit, db)


@router.get(
    "/{channel_id}",
    response_model=ChannelDetailResponse,
    summary="Get channel by ID",
    description="Get a single channel by its ID"
)
async def get_channel(
    channel_id: int,
    db: AsyncSession = Depends(get_db)
) -> ChannelDetailResponse:
    """
    Get channel by ID.
    
    Args:
        channel_id: Channel ID
        db: Database session
        
    Returns:
        Channel details
    """
    try:
        channel = await channel_service.get_by_id(db, channel_id)
        
        return ChannelDetailResponse(
            status=True,
            statusCode=200,
            message="Success",
            data=ChannelResponse.model_validate(channel)
        )
    except StreamHubException as e:
        raise e


@router.post(
    "/create-channel",
    response_model=ChannelDetailResponse,
    status_code=status.HTTP_201_CREATED,
    summary="Create a new channel",
    description="Create a new channel with name, category, and optional description/logo"
)
async def create_channel(
    channel_data: ChannelCreate,
    db: AsyncSession = Depends(get_db)
) -> ChannelDetailResponse:
    """
    Create a new channel.
    
    Args:
        channel_data: Channel creation data
        db: Database session
        
    Returns:
        Created channel
    """
    try:
        channel = await channel_service.create(db, channel_data)
        
        return ChannelDetailResponse(
            status=True,
            statusCode=201,
            message="Channel created successfully",
            data=ChannelResponse.model_validate(channel)
        )
    except StreamHubException as e:
        raise e


@router.post(
    "/",
    response_model=ChannelDetailResponse,
    status_code=status.HTTP_201_CREATED,
    summary="Create a new channel (alternative endpoint)",
    description="Create a new channel - same as /create-channel"
)
async def create_channel_alt(
    channel_data: ChannelCreate,
    db: AsyncSession = Depends(get_db)
) -> ChannelDetailResponse:
    """Create a new channel (alternative endpoint)."""
    return await create_channel(channel_data, db)


@router.put(
    "/{channel_id}",
    response_model=ChannelDetailResponse,
    summary="Update a channel",
    description="Update an existing channel by ID"
)
async def update_channel(
    channel_id: int,
    channel_data: ChannelUpdate,
    db: AsyncSession = Depends(get_db)
) -> ChannelDetailResponse:
    """
    Update channel.
    
    Args:
        channel_id: Channel ID
        channel_data: Channel update data
        db: Database session
        
    Returns:
        Updated channel
    """
    try:
        channel = await channel_service.update(db, channel_id, channel_data)
        
        return ChannelDetailResponse(
            status=True,
            statusCode=200,
            message="Channel updated successfully",
            data=ChannelResponse.model_validate(channel)
        )
    except StreamHubException as e:
        raise e


@router.put(
    "/",
    response_model=ChannelDetailResponse,
    summary="Update a channel (alternative endpoint)",
    description="Update channel without specifying ID in URL (requires ID in body)"
)
async def update_channel_alt(
    channel_data: ChannelUpdate,
    db: AsyncSession = Depends(get_db)
) -> ChannelDetailResponse:
    """Update channel (alternative endpoint - not recommended)."""
    # This endpoint exists for backward compatibility but is not recommended
    # because ID should be in URL path
    raise StreamHubException(
        "Please use PUT /{channel_id} instead",
        status_code=400
    )


@router.delete(
    "/{channel_id}",
    response_model=dict,
    summary="Delete a channel",
    description="Delete a channel by ID"
)
async def delete_channel(
    channel_id: int,
    db: AsyncSession = Depends(get_db)
) -> dict:
    """
    Delete channel.
    
    Args:
        channel_id: Channel ID
        db: Database session
        
    Returns:
        Success message
    """
    try:
        await channel_service.delete(db, channel_id)
        
        return {
            "status": True,
            "statusCode": 200,
            "message": f"Channel {channel_id} deleted successfully"
        }
    except StreamHubException as e:
        raise e
