"""
Video API routes - CRUD + Upload.
"""
import os
import uuid
from typing import Optional
from pathlib import Path
from datetime import datetime

from fastapi import APIRouter, Depends, UploadFile, File, Form, HTTPException
from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from app.models.video import Video
from app.models.channel import Channel
from app.schemas.video import VideoCreate, VideoUpdate, VideoResponse, VideoListResponse
from app.db.session import get_db
from app.core.auth import require_auth


router = APIRouter(prefix="/videos", tags=["videos"])

# Upload directory
UPLOAD_DIR = Path("/app/uploads/videos")
UPLOAD_DIR.mkdir(parents=True, exist_ok=True)


@router.post("/upload", response_model=VideoResponse)
async def upload_video(
    title: str = Form(...),
    channel_id: int = Form(...),
    category: str = Form(default="entertainment"),
    description: Optional[str] = Form(None),
    file: UploadFile = File(...),
    db: AsyncSession = Depends(get_db),
    current_user: dict = Depends(require_auth)
):
    """
    Upload video file with UUID filename.
    
    - Generates UUID v4 for filename
    - Saves to /app/uploads/videos/
    - Stores metadata in database
    """
    
    # Validate channel exists
    result = await db.execute(select(Channel).where(Channel.id == channel_id))
    channel = result.scalar_one_or_none()
    if not channel:
        raise HTTPException(status_code=404, detail="Channel not found")
    
    # Validate file type
    if not file.filename:
        raise HTTPException(status_code=400, detail="No file provided")
    
    if not file.filename.lower().endswith('.mp4'):
        raise HTTPException(status_code=400, detail="Only MP4 files are supported")
    
    # Generate UUID for filename
    file_extension = Path(file.filename).suffix or '.mp4'
    uuid_filename = f"{uuid.uuid4()}{file_extension}"
    file_path = UPLOAD_DIR / uuid_filename
    
    # Save file
    try:
        contents = await file.read()
        with open(file_path, "wb") as f:
            f.write(contents)
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Failed to save file: {str(e)}")
    
    # Create video record
    video_data = {
        "title": title,
        "description": description,
        "youtube_id": None,  # No YouTube ID for uploaded videos
        "channel_id": channel_id,
        "video_url": f"/uploads/videos/{uuid_filename}",
        "thumbnail_url": None,  # Will be generated separately
        "is_active": True,
    }
    
    video = Video(**video_data)
    db.add(video)
    await db.commit()
    await db.refresh(video)
    
    return VideoResponse(
        id=video.id,
        title=video.title,
        description=video.description,
        youtube_id=video.youtube_id,
        channel_id=video.channel_id,
        thumbnail_url=video.thumbnail_url,
        duration=video.duration,
        view_count=video.view_count,
        is_live=video.is_live,
        is_active=video.is_active,
        created_at=video.created_at,
        updated_at=video.updated_at
    )


@router.post("/upload/thumbnail/{video_id}", response_model=dict)
async def upload_thumbnail(
    video_id: int,
    file: UploadFile = File(...),
    db: AsyncSession = Depends(get_db),
    current_user: dict = Depends(require_auth)
):
    """
    Upload thumbnail for a video.
    
    Accepts image files (jpg, png, webp).
    """
    
    # Get video
    result = await db.execute(select(Video).where(Video.id == video_id))
    video = result.scalar_one_or_none()
    if not video:
        raise HTTPException(status_code=404, detail="Video not found")
    
    # Validate file type
    allowed_extensions = {'.jpg', '.jpeg', '.png', '.webp'}
    file_extension = Path(file.filename).suffix.lower() if file.filename else ''
    
    if file_extension not in allowed_extensions:
        raise HTTPException(
            status_code=400, 
            detail=f"Invalid file type. Allowed: {', '.join(allowed_extensions)}"
        )
    
    # Generate thumbnail filename
    thumbnail_filename = f"{uuid.uuid4()}{file_extension}"
    thumbnail_path = UPLOAD_DIR.parent / "thumbnails" / thumbnail_filename
    thumbnail_path.parent.mkdir(exist_ok=True)
    
    # Save thumbnail
    try:
        contents = await file.read()
        with open(thumbnail_path, "wb") as f:
            f.write(contents)
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Failed to save thumbnail: {str(e)}")
    
    # Update video with thumbnail URL
    video.thumbnail_url = f"/uploads/thumbnails/{thumbnail_filename}"
    await db.commit()
    
    return {
        "status": True,
        "thumbnail_url": video.thumbnail_url
    }


# Include existing CRUD routes
from app.api.videos import *

# Keep all existing endpoints
