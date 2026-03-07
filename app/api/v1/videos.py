"""
Video API routes - With Upload Support + FFmpeg Integration + Multi-format Support.
"""
import uuid
import json
import base64
import io
from typing import Optional
from pathlib import Path
from datetime import datetime
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
import os
UPLOAD_DIR = Path(os.getcwd()) / "uploads" / "videos"
UPLOAD_DIR.mkdir(parents=True, exist_ok=True)

# Allowed file extensions
ALLOWED_EXTENSIONS = {'.mp4', '.jpg', '.jpeg', '.png', '.bmp', '.gif'}


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

        # Manually construct response to include category from channel
        video_responses = []
        for video in videos:
            video_dict = {
                "id": video.id,
                "title": video.title,
                "description": video.description,
                "youtube_id": video.youtube_id,
                "channel_id": video.channel_id,
                "video_url": video.video_url,
                "thumbnail_url": video.thumbnail_url,
                "thumbnail_data": video.thumbnail_data,
                "duration": float(video.duration) if video.duration else None,
                "view_count": video.view_count,
                "is_live": video.is_live,
                "is_active": video.is_active,
                "width": video.width,
                "height": video.height,
                "video_codec": video.video_codec,
                "video_bitrate": video.video_bitrate,
                "audio_codec": video.audio_codec,
                "audio_bitrate": video.audio_bitrate,
                "fps": float(video.fps) if video.fps else None,
                "category": video.channel.category if video.channel else None,
                "tags": video.tags if hasattr(video, 'tags') else None,
                "expiry_date": video.expiry_date if hasattr(video, 'expiry_date') else None,
                "content_type": video.content_type if hasattr(video, 'content_type') else None,
                "created_at": video.created_at,
                "updated_at": video.updated_at,
            }
            video_responses.append(VideoResponse(**video_dict))

        return VideoListResponse(
            status=True,
            statusCode=200,
            message="Success",
            data=video_responses,
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
    summary="Upload content file with FFmpeg/Pillow processing",
    description="Upload MP4 video or image file with UUID filename, auto-generate thumbnail and extract metadata. Supports MP4, JPG, JPEG, PNG, BMP, GIF."
)
async def upload_video(
    title: str = Form(...),
    channel_id: int = Form(...),
    category: str = Form(default="entertainment"),
    description: Optional[str] = Form(None),
    expiry_date: Optional[str] = Form(None),
    tags: Optional[str] = Form(None),
    file: UploadFile = File(...),
    thumbnail: Optional[UploadFile] = File(None),
    db: AsyncSession = Depends(get_db)
):
    """
    Upload content file (video or image) with UUID filename, auto-generate thumbnail, and extract metadata.
    
    Supports:
    - Videos: MP4 with FFmpeg thumbnail generation and metadata extraction
    - Images: JPG, JPEG, PNG, BMP, GIF with Pillow thumbnail generation
    - Tags: JSON array or comma-separated string
    - Expiry Date: Optional date string
    
    Args:
        title: Content title
        channel_id: Channel ID
        category: Content category
        description: Content description (optional)
        expiry_date: Expiry date in YYYY-MM-DD format (optional)
        tags: Tags as JSON array or comma-separated string (optional)
        file: Video or image file
        thumbnail: Custom thumbnail image file (optional)
        db: Database session
        
    Returns:
        Created content record with metadata
    """
    
    # Validate file type
    if not file.filename:
        raise HTTPException(status_code=400, detail="No file provided")
    
    file_extension = Path(file.filename).suffix.lower()
    if file_extension not in ALLOWED_EXTENSIONS:
        raise HTTPException(
            status_code=400, 
            detail=f"Unsupported file type '{file_extension}'. Allowed: {', '.join(sorted(ALLOWED_EXTENSIONS))}"
        )
    
    # Generate UUID for filename
    uuid_filename = f"{uuid.uuid4()}{file_extension}"
    file_path = UPLOAD_DIR / uuid_filename
    
    # Save file
    try:
        contents = await file.read()
        with open(file_path, "wb") as f:
            f.write(contents)
        print(f"✓ File saved: {uuid_filename} ({len(contents)} bytes)")
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Failed to save file: {str(e)}")
    
    # Determine content type and process accordingly
    is_video = file_extension == '.mp4'
    content_type = "video" if is_video else "image"
    
    # Initialize metadata
    thumbnail_data = None
    metadata = {}
    
    if is_video:
        # Process video with FFmpeg
        try:
            # Extract metadata
            metadata = ffmpeg_service.extract_metadata(str(file_path))
            print(f"✓ Video metadata: {metadata.get('width')}x{metadata.get('height')} @ {metadata.get('fps')} fps, {metadata.get('duration')}s")
            
            # Generate thumbnail
            thumbnail_data = ffmpeg_service.generate_thumbnail(str(file_path))
            if thumbnail_data:
                print(f"✓ Video thumbnail generated (base64: {len(thumbnail_data)} chars)")
            
        except Exception as e:
            print(f"⚠ FFmpeg processing failed: {str(e)}")
            # Set basic metadata even if FFmpeg fails
            metadata = {"duration": None, "fps": None, "video_codec": None, "audio_codec": None}
    else:
        # Process image with Pillow
        try:
            from PIL import Image
            
            with Image.open(file_path) as img:
                metadata = {
                    "width": img.width,
                    "height": img.height,
                    "duration": None,
                    "fps": None,
                    "video_codec": None,
                    "audio_codec": None,
                }
                print(f"✓ Image metadata: {img.width}x{img.height}")
                
                # Generate thumbnail
                img_copy = img.copy()
                img_copy.thumbnail((320, 180))
                buffer = io.BytesIO()
                img_copy.save(buffer, format='JPEG')
                thumbnail_data = base64.b64encode(buffer.getvalue()).decode('utf-8')
                print(f"✓ Image thumbnail generated (base64: {len(thumbnail_data)} chars)")
                
        except Exception as e:
            print(f"⚠ Image processing failed: {str(e)}")
            metadata = {"width": None, "height": None, "duration": None, "fps": None, "video_codec": None, "audio_codec": None}
    
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
    
    # Parse tags
    tags_list = None
    if tags:
        try:
            # Try to parse as JSON array
            tags_list = json.loads(tags)
            if not isinstance(tags_list, list):
                tags_list = tags_list.split(',')
        except json.JSONDecodeError:
            # Fallback to comma-separated
            tags_list = [t.strip() for t in tags.split(',') if t.strip()]
        print(f"✓ Tags parsed: {tags_list}")
    
    # Parse expiry date
    expiry_date_obj = None
    if expiry_date:
        try:
            expiry_date_obj = datetime.strptime(expiry_date, '%Y-%m-%d').date()
            print(f"✓ Expiry date: {expiry_date_obj}")
        except ValueError as e:
            print(f"⚠ Invalid expiry date format: {expiry_date} (expected YYYY-MM-DD)")
    
    # Verify channel exists
    from sqlalchemy import select
    from app.models.channel import Channel
    from app.models.video import Video
    
    result = await db.execute(select(Channel).where(Channel.id == channel_id))
    channel = result.scalar_one_or_none()
    if not channel:
        # Clean up uploaded file if channel doesn't exist
        file_path.unlink(missing_ok=True)
        raise HTTPException(status_code=404, detail="Channel not found")
    
    # Build content data with metadata
    content_data = {
        "title": title,
        "description": description,
        "youtube_id": None,
        "channel_id": channel_id,
        "video_url": f"/uploads/videos/{uuid_filename}",
        "thumbnail_url": thumbnail_url,
        "thumbnail_data": thumbnail_data,
        "duration": metadata.get("duration"),
        "width": metadata.get("width"),
        "height": metadata.get("height"),
        "fps": metadata.get("fps"),
        "video_codec": metadata.get("video_codec"),
        "audio_codec": metadata.get("audio_codec"),
        "is_active": True,
        "tags": tags_list,
        "expiry_date": expiry_date_obj,
        "content_type": content_type,
    }
    
    content = Video(**content_data)
    db.add(content)
    await db.commit()
    await db.refresh(content)
    
    print(f"✓ Content record created: ID={content.id}, Type={content_type}, Title={title}")
    
    # Construct response with category
    response_data = content_data.copy()
    response_data["id"] = content.id
    response_data["view_count"] = content.view_count
    response_data["is_live"] = content.is_live
    response_data["created_at"] = content.created_at
    response_data["updated_at"] = content.updated_at
    response_data["category"] = channel.category
    
    return VideoDetailResponse(
        status=True,
        statusCode=201,
        message=f"{content_type.capitalize()} uploaded successfully. Filename: {uuid_filename}",
        data=VideoResponse(**response_data)
    )
