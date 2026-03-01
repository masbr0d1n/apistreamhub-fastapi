"""
Video schemas - request/response validation.
"""
from pydantic import BaseModel, Field, field_validator
from typing import Optional
from datetime import datetime


class VideoBase(BaseModel):
    """Base video schema."""
    
    title: str = Field(..., min_length=1, max_length=500, description="Video title")
    description: Optional[str] = Field(None, description="Video description")
    youtube_id: Optional[str] = Field(None, max_length=255, description="YouTube video ID or filename")
    channel_id: int = Field(..., gt=0, description="Channel ID")
    thumbnail_url: Optional[str] = Field(None, description="Thumbnail URL")
    duration: Optional[float] = Field(None, ge=0, description="Duration in seconds")
    view_count: int = Field(default=0, ge=0, description="View count")
    is_live: bool = Field(default=False, description="Is live stream")
    is_active: bool = Field(default=True, description="Is active")


class VideoCreate(VideoBase):
    """Schema for video creation."""
    pass


class VideoUpdate(BaseModel):
    """Schema for video update."""
    
    title: Optional[str] = Field(None, min_length=1, max_length=500)
    description: Optional[str] = None
    thumbnail_url: Optional[str] = None
    duration: Optional[float] = Field(None, ge=0)
    view_count: Optional[int] = Field(None, ge=0)
    is_live: Optional[bool] = None
    is_active: Optional[bool] = None


class VideoResponse(BaseModel):
    """Schema for video response."""
    
    id: int
    title: str
    description: Optional[str]
    youtube_id: Optional[str]
    channel_id: int
    video_url: Optional[str] = None  # URL for uploaded video files
    thumbnail_url: Optional[str] = None
    duration: Optional[float]
    view_count: int
    is_live: bool
    is_active: bool
    
    # Video metadata
    width: Optional[int] = None
    height: Optional[int] = None
    video_codec: Optional[str] = None
    video_bitrate: Optional[int] = None
    audio_codec: Optional[str] = None
    audio_bitrate: Optional[int] = None
    fps: Optional[float] = None
    
    created_at: datetime
    updated_at: datetime
    
    class Config:
        from_attributes = True


class VideoListResponse(BaseModel):
    """Schema for video list response."""
    
    status: bool = True
    statusCode: int = 200
    message: str = "Success"
    data: list[VideoResponse]
    count: int


class VideoDetailResponse(BaseModel):
    """Schema for video detail response."""
    
    status: bool = True
    statusCode: int = 200
    message: str = "Success"
    data: VideoResponse
