"""
Video API routes.
"""
from typing import Optional
from fastapi import APIRouter, Depends, status, Query
from sqlalchemy.ext.asyncio import AsyncSession

from app.db.base import get_db
from app.schemas.video import (
    VideoCreate,
    VideoUpdate,
    VideoResponse,
    VideoListResponse,
    VideoDetailResponse
)
from app.services.video_service import VideoService
from app.core.exceptions import StreamHubException


router = APIRouter(prefix="/videos", tags=["videos"])
video_service = VideoService()


@router.get(
    "/",
    response_model=VideoListResponse,
    summary="List all videos",
    description="Get all videos with optional filtering and pagination"
)
async def list_videos(
    skip: int = Query(0, ge=0, description="Number of records to skip"),
    limit: int = Query(100, ge=1, le=100, description="Maximum number of records to return"),
    channel_id: Optional[int] = Query(None, description="Filter by channel ID"),
    is_active: Optional[bool] = Query(None, description="Filter by active status"),
    db: AsyncSession = Depends(get_db)
) -> VideoListResponse:
    """
    Get all videos.
    
    Args:
        skip: Number of records to skip
        limit: Maximum number of records to return
        channel_id: Filter by channel ID
        is_active: Filter by active status
        db: Database session
        
    Returns:
        List of videos
    """
    try:
        videos = await video_service.get_all(db, skip, limit, channel_id, is_active)
        
        return VideoListResponse(
            status=True,
            statusCode=200,
            message="Success",
            data=[VideoResponse.model_validate(v) for v in videos],
            count=len(videos)
        )
    except StreamHubException as e:
        raise e


@router.get(
    "/{video_id}",
    response_model=VideoDetailResponse,
    summary="Get video by ID",
    description="Get a single video by its ID"
)
async def get_video(
    video_id: int,
    db: AsyncSession = Depends(get_db)
) -> VideoDetailResponse:
    """
    Get video by ID.
    
    Args:
        video_id: Video ID
        db: Database session
        
    Returns:
        Video details
    """
    try:
        video = await video_service.get_by_id(db, video_id)
        
        return VideoDetailResponse(
            status=True,
            statusCode=200,
            message="Success",
            data=VideoResponse.model_validate(video)
        )
    except StreamHubException as e:
        raise e


@router.post(
    "/",
    response_model=VideoDetailResponse,
    status_code=status.HTTP_201_CREATED,
    summary="Create a new video",
    description="Create a new video with title, YouTube ID, and channel"
)
async def create_video(
    video_data: VideoCreate,
    db: AsyncSession = Depends(get_db)
) -> VideoDetailResponse:
    """
    Create a new video.
    
    Args:
        video_data: Video creation data
        db: Database session
        
    Returns:
        Created video
    """
    try:
        video = await video_service.create(db, video_data)
        
        return VideoDetailResponse(
            status=True,
            statusCode=201,
            message="Video created successfully",
            data=VideoResponse.model_validate(video)
        )
    except StreamHubException as e:
        raise e


@router.put(
    "/{video_id}",
    response_model=VideoDetailResponse,
    summary="Update a video",
    description="Update an existing video by ID"
)
async def update_video(
    video_id: int,
    video_data: VideoUpdate,
    db: AsyncSession = Depends(get_db)
) -> VideoDetailResponse:
    """
    Update video.
    
    Args:
        video_id: Video ID
        video_data: Video update data
        db: Database session
        
    Returns:
        Updated video
    """
    try:
        video = await video_service.update(db, video_id, video_data)
        
        return VideoDetailResponse(
            status=True,
            statusCode=200,
            message="Video updated successfully",
            data=VideoResponse.model_validate(video)
        )
    except StreamHubException as e:
        raise e


@router.delete(
    "/{video_id}",
    response_model=dict,
    summary="Delete a video",
    description="Delete a video by ID"
)
async def delete_video(
    video_id: int,
    db: AsyncSession = Depends(get_db)
) -> dict:
    """
    Delete video.
    
    Args:
        video_id: Video ID
        db: Database session
        
    Returns:
        Success message
    """
    try:
        await video_service.delete(db, video_id)
        
        return {
            "status": True,
            "statusCode": 200,
            "message": f"Video {video_id} deleted successfully"
        }
    except StreamHubException as e:
        raise e


@router.post(
    "/{video_id}/view",
    response_model=VideoDetailResponse,
    summary="Increment video view count",
    description="Increment the view count for a video"
)
async def increment_view_count(
    video_id: int,
    db: AsyncSession = Depends(get_db)
) -> VideoDetailResponse:
    """
    Increment video view count.
    
    Args:
        video_id: Video ID
        db: Database session
        
    Returns:
        Updated video with incremented view count
    """
    try:
        video = await video_service.increment_view_count(db, video_id)
        
        return VideoDetailResponse(
            status=True,
            statusCode=200,
            message="View count incremented",
            data=VideoResponse.model_validate(video)
        )
    except StreamHubException as e:
        raise e


@router.get(
    "/youtube/{youtube_id}",
    response_model=VideoDetailResponse,
    summary="Get video by YouTube ID",
    description="Get a video by its YouTube ID"
)
async def get_video_by_youtube_id(
    youtube_id: str,
    db: AsyncSession = Depends(get_db)
) -> VideoDetailResponse:
    """
    Get video by YouTube ID.
    
    Args:
        youtube_id: YouTube video ID
        db: Database session
        
    Returns:
        Video details
    """
    try:
        video = await video_service.get_by_youtube_id(db, youtube_id)
        
        if not video:
            raise StreamHubException(f"Video with YouTube ID '{youtube_id}' not found", status_code=404)
        
        return VideoDetailResponse(
            status=True,
            statusCode=200,
            message="Success",
            data=VideoResponse.model_validate(video)
        )
    except StreamHubException as e:
        raise e
