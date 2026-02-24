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
    youtube_id: str = Field(..., min_length=11, max_length=11, description="YouTube video ID (11 characters)")
    channel_id: int = Field(..., gt=0, description="Channel ID")
    thumbnail_url: Optional[str] = Field(None, description="Thumbnail URL")
    duration: Optional[int] = Field(None, ge=0, description="Duration in seconds")
    view_count: int = Field(default=0, ge=0, description="View count")
    is_live: bool = Field(default=False, description="Is live stream")
    is_active: bool = Field(default=True, description="Is active")
    
    @field_validator('youtube_id')
    @classmethod
    def validate_youtube_id(cls, v: str) -> str:
        """Validate YouTube ID is exactly 11 characters."""
        if len(v) != 11:
            raise ValueError('YouTube ID must be exactly 11 characters')
        return v


class VideoCreate(VideoBase):
    """Schema for video creation."""
    pass


class VideoUpdate(BaseModel):
    """Schema for video update."""
    
    title: Optional[str] = Field(None, min_length=1, max_length=500)
    description: Optional[str] = None
    thumbnail_url: Optional[str] = None
    duration: Optional[int] = Field(None, ge=0)
    view_count: Optional[int] = Field(None, ge=0)
    is_live: Optional[bool] = None
    is_active: Optional[bool] = None


class VideoResponse(BaseModel):
    """Schema for video response."""
    
    id: int
    title: str
    description: Optional[str]
    youtube_id: str
    channel_id: int
    thumbnail_url: Optional[str]
    duration: Optional[int]
    view_count: int
    is_live: bool
    is_active: bool
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
