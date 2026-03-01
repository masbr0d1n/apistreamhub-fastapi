"""
Playlist Schemas
Request and response models for playlists
"""
from datetime import datetime
from typing import Optional, List
from pydantic import BaseModel, Field


class PlaylistBase(BaseModel):
    """Base playlist schema"""
    name: str = Field(..., min_length=1, max_length=255)
    channel_id: int = Field(..., gt=0)
    start_time: datetime
    description: Optional[str] = None


class PlaylistCreate(PlaylistBase):
    """Schema for creating a playlist"""
    pass


class PlaylistUpdate(BaseModel):
    """Schema for updating a playlist"""
    name: Optional[str] = Field(None, min_length=1, max_length=255)
    channel_id: Optional[int] = Field(None, gt=0)
    start_time: Optional[datetime] = None
    status: Optional[str] = None
    description: Optional[str] = None


class PlaylistResponse(PlaylistBase):
    """Schema for playlist response"""
    id: int
    status: str
    video_count: int
    created_at: datetime
    updated_at: datetime
    channel_name: Optional[str] = None

    class Config:
        from_attributes = True


class PlaylistListItem(BaseModel):
    """Schema for single playlist item in list"""
    id: int
    name: str
    channel_id: int
    channel_name: str
    start_time: datetime
    status: str
    video_count: int
    created_at: datetime
    updated_at: datetime

    class Config:
        from_attributes = True


class PlaylistListResponse(BaseModel):
    """Schema for playlist list response"""
    status: bool = True
    statusCode: int = 200
    message: str = "Success"
    data: List[PlaylistListItem]


class PlaylistDetailResponse(BaseModel):
    """Schema for single playlist response"""
    status: bool = True
    statusCode: int = 200
    message: str = "Success"
    data: PlaylistResponse


class PlaylistVideoAdd(BaseModel):
    """Schema for adding video to playlist"""
    video_id: int = Field(..., gt=0)
    order: Optional[int] = 0


class PlaylistVideoResponse(BaseModel):
    """Schema for playlist video response"""
    id: int
    video_id: int
    video_title: Optional[str] = None
    video_url: Optional[str] = None
    order: int

    class Config:
        from_attributes = True
