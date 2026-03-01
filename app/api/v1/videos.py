"""
Video API routes - With Upload Support + FFmpeg Integration.
"""
import uuid
from typing import Optional
from pathlib import Path
from fastapi import APIRouter, Depends, status, Query, UploadFile, File, Form, HTTPException
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
from app.services.ffmpeg_service import ffmpeg_service
from app.core.exceptions import StreamHubException


router = APIRouter(prefix="/videos", tags=["videos"])
video_service = VideoService()

# Configure upload directory
UPLOAD_DIR = Path("/app/uploads/videos")
UPLOAD_DIR.mkdir(parents=True, exist_ok=True)


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
    category: Optional[str] = Query(None, description="Filter by channel category"),
    search: Optional[str] = Query(None, description="Search by title or description"),
    db: AsyncSession = Depends(get_db)
) -> VideoListResponse:
    """
    Get all videos.

    Args:
        skip: Number of records to skip
        limit: Maximum number of records to return
        channel_id: Filter by channel ID
        is_active: Filter by active status
        category: Filter by channel category
        search: Search by title or description
        db: Database session

    Returns:
        List of videos
    """
    try:
        videos = await video_service.get_all(
            db, skip, limit, channel_id, is_active, category, search
        )

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


@router.put(
    "/{video_id}",
    response_model=VideoDetailResponse,
    summary="Update a video",
    description="Update video by ID"
)
async def update_video(
    video_id: int,
    video_update: VideoUpdate,
    db: AsyncSession = Depends(get_db)
) -> VideoDetailResponse:
    """
    Update video.
    
    Args:
        video_id: Video ID
        video_update: Video update data
        db: Database session
        
    Returns:
        Updated video
    """
    try:
        video = await video_service.update(db, video_id, video_update)
        
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
    Increment view count.
    
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


@router.post(
    "/upload",
    response_model=VideoDetailResponse,
    summary="Upload video file with FFmpeg processing",
    description="Upload MP4 video file with UUID filename, auto-generate thumbnail and extract metadata"
)
async def upload_video(
    title: str = Form(...),
    channel_id: int = Form(...),
    category: str = Form(default="entertainment"),
    description: Optional[str] = Form(None),
    file: UploadFile = File(...),
    thumbnail: Optional[UploadFile] = File(None),
    db: AsyncSession = Depends(get_db)
):
    """
    Upload video file with UUID filename, auto-generate thumbnail, and extract metadata.
    
    - Generates UUID v4 for filename
    - Saves to /app/uploads/videos/
    - Auto-generates thumbnail using FFmpeg
    - Extracts metadata (resolution, fps, codecs, bitrate, duration)
    - Stores everything in database
    - Optionally accepts custom thumbnail image
    
    Args:
        title: Video title
        channel_id: Channel ID
        category: Video category
        description: Video description (optional)
        file: MP4 video file
        thumbnail: Custom thumbnail image file (optional)
        db: Database session
        
    Returns:
        Created video record with metadata
    """
    
    # Validate file type
    if not file.filename:
        raise HTTPException(status_code=400, detail="No file provided")
    
    file_extension = Path(file.filename).suffix.lower()
    if file_extension != '.mp4':
        raise HTTPException(status_code=400, detail="Only MP4 files are supported")
    
    # Generate UUID for filename
    uuid_filename = f"{uuid.uuid4()}{file_extension}"
    file_path = UPLOAD_DIR / uuid_filename
    
    # Save video file
    try:
        contents = await file.read()
        with open(file_path, "wb") as f:
            f.write(contents)
        print(f"✓ Video saved: {uuid_filename}")
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Failed to save file: {str(e)}")
    
    # Process video with FFmpeg
    thumbnail_data = None
    metadata = {}
    
    try:
        # Extract metadata
        metadata = ffmpeg_service.extract_metadata(str(file_path))
        print(f"✓ Metadata extracted: {metadata.get('width')}x{metadata.get('height')} @ {metadata.get('fps')} fps")
        
        # Generate thumbnail
        thumbnail_data = ffmpeg_service.generate_thumbnail(str(file_path))
        if thumbnail_data:
            print(f"✓ Thumbnail generated (base64: {len(thumbnail_data)} chars)")
        
    except Exception as e:
        print(f"⚠ FFmpeg processing failed: {str(e)}")
        # Continue without metadata/thumbnail
    
    # Handle custom thumbnail if provided
    thumbnail_url = None
    if thumbnail and thumbnail.filename:
        thumbnail_ext = Path(thumbnail.filename).suffix.lower()
        thumbnail_filename = f"{uuid.uuid4()}{thumbnail_ext}"
        thumbnail_dir = UPLOAD_DIR.parent / "thumbnails"
        thumbnail_dir.mkdir(exist_ok=True)
        thumbnail_path = thumbnail_dir / thumbnail_filename
        
        try:
            thumb_contents = await thumbnail.read()
            with open(thumbnail_path, "wb") as f:
                f.write(thumb_contents)
            thumbnail_url = f"/uploads/thumbnails/{thumbnail_filename}"
            print(f"✓ Custom thumbnail saved: {thumbnail_filename}")
        except Exception as e:
            print(f"⚠ Failed to save custom thumbnail: {str(e)}")
    
    # Create video record
    from sqlalchemy import select
    from app.models.channel import Channel
    from app.models.video import Video
    
    # Verify channel exists
    result = await db.execute(select(Channel).where(Channel.id == channel_id))
    channel = result.scalar_one_or_none()
    if not channel:
        # Clean up uploaded file if channel doesn't exist
        file_path.unlink(missing_ok=True)
        raise HTTPException(status_code=404, detail="Channel not found")
    
    # Build video data with metadata
    video_data = {
        "title": title,
        "description": description,
        "youtube_id": None,  # No YouTube ID for uploaded videos
        "channel_id": channel_id,
        "video_url": f"/uploads/videos/{uuid_filename}",
        "thumbnail_url": thumbnail_url,
        "thumbnail_data": thumbnail_data,  # Base64 from FFmpeg
        "duration": metadata.get("duration"),
        "width": metadata.get("width"),
        "height": metadata.get("height"),
        "fps": metadata.get("fps"),
        "video_codec": metadata.get("video_codec"),
        "audio_codec": metadata.get("audio_codec"),
        "is_active": True,
    }
    
    video = Video(**video_data)
    db.add(video)
    await db.commit()
    await db.refresh(video)
    
    print(f"✓ Video record created: ID={video.id}, Title={title}")
    
    return VideoDetailResponse(
        status=True,
        statusCode=201,
        message=f"Video uploaded successfully. Filename: {uuid_filename}",
        data=VideoResponse.model_validate(video)
    )
