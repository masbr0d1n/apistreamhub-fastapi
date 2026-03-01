"""
Streaming control API routes.
Handles channel on-air/off-air control.
"""
from fastapi import APIRouter, Depends, status
from sqlalchemy.ext.asyncio import AsyncSession
from datetime import datetime
import logging

from app.db.base import get_db
from app.schemas.auth import UserResponse
from app.schemas.streaming import StreamingResponse
from app.services.streaming_service import StreamingService
from app.core.exceptions import StreamHubException
from app.core.security import get_current_user


router = APIRouter(prefix="/streaming", tags=["streaming"])
streaming_service = StreamingService()
logger = logging.getLogger(__name__)


@router.post(
    "/channels/{channel_id}/on-air",
    response_model=StreamingResponse,
    status_code=status.HTTP_200_OK,
    summary="Turn on channel for streaming",
    description="Start streaming for the specified channel"
)
async def turn_on_air(
    channel_id: int,
    db: AsyncSession = Depends(get_db),
    current_user: UserResponse = Depends(get_current_user)
) -> StreamingResponse:
    """
    Turn on channel for streaming.
    
    This endpoint:
    1. Updates channel status to 'on-air'
    2. Triggers streaming server (nginx-rtmp/ffmpeg)
    3. Logs the event
    4. Returns current status
    
    Args:
        channel_id: Channel ID to turn on
        db: Database session
        current_user: Authenticated user
        
    Returns:
        Streaming status response
    """
    try:
        logger.info(f"User {current_user.username} turning on channel {channel_id}")
        
        result = await streaming_service.turn_on_air(db, channel_id, current_user.id)
        
        return StreamingResponse(
            status=True,
            statusCode=200,
            message=f"Channel {channel_id} is now on-air",
            data=result
        )
        
    except StreamHubException as e:
        logger.error(f"Error turning on channel {channel_id}: {e.message}")
        raise e
    except Exception as e:
        logger.error(f"Unexpected error turning on channel {channel_id}: {str(e)}")
        raise StreamHubException(
            message=f"Failed to turn on channel: {str(e)}",
            statusCode=500
        )


@router.post(
    "/channels/{channel_id}/off-air",
    response_model=StreamingResponse,
    status_code=status.HTTP_200_OK,
    summary="Turn off channel streaming",
    description="Stop streaming for the specified channel"
)
async def turn_off_air(
    channel_id: int,
    db: AsyncSession = Depends(get_db),
    current_user: UserResponse = Depends(get_current_user)
) -> StreamingResponse:
    """
    Turn off channel streaming.
    
    This endpoint:
    1. Updates channel status to 'off-air'
    2. Stops streaming server
    3. Logs the event
    4. Returns current status
    
    Args:
        channel_id: Channel ID to turn off
        db: Database session
        current_user: Authenticated user
        
    Returns:
        Streaming status response
    """
    try:
        logger.info(f"User {current_user.username} turning off channel {channel_id}")
        
        result = await streaming_service.turn_off_air(db, channel_id, current_user.id)
        
        return StreamingResponse(
            status=True,
            statusCode=200,
            message=f"Channel {channel_id} is now off-air",
            data=result
        )
        
    except StreamHubException as e:
        logger.error(f"Error turning off channel {channel_id}: {e.message}")
        raise e
    except Exception as e:
        logger.error(f"Unexpected error turning off channel {channel_id}: {str(e)}")
        raise StreamHubException(
            message=f"Failed to turn off channel: {str(e)}",
            statusCode=500
        )


@router.get(
    "/channels/{channel_id}/status",
    response_model=StreamingResponse,
    summary="Get channel streaming status",
    description="Get current streaming status of a channel"
)
async def get_channel_status(
    channel_id: int,
    db: AsyncSession = Depends(get_db),
    current_user: UserResponse = Depends(get_current_user)
) -> StreamingResponse:
    """
    Get current streaming status of a channel.
    
    Args:
        channel_id: Channel ID to check
        db: Database session
        current_user: Authenticated user
        
    Returns:
        Current streaming status
    """
    try:
        status_data = await streaming_service.get_status(db, channel_id)
        
        return StreamingResponse(
            status=True,
            statusCode=200,
            message="Channel status retrieved",
            data=status_data
        )
        
    except Exception as e:
        logger.error(f"Error getting status for channel {channel_id}: {str(e)}")
        raise StreamHubException(
            message=f"Failed to get channel status: {str(e)}",
            statusCode=500
        )
