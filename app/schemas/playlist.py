"""
Playlist Schemas
Pydantic models for playlist API
"""

from pydantic import BaseModel, Field
from typing import Optional, List
from datetime import datetime


# ==================== Playlist ====================

class PlaylistBase(BaseModel):
    name: str = Field(..., min_length=1, max_length=255)
    description: Optional[str] = None
    default_duration: float = Field(default=10, ge=1, le=3600)  # seconds
    transition: str = Field(default="fade", pattern="^(fade|slide|none)$")
    loop: bool = True


class PlaylistItemCreateSimple(BaseModel):
    """Simple item schema for playlist creation"""
    media_id: str
    name: str
    duration: float
    order: int
    media_type: str = "video"


class PlaylistCreate(PlaylistBase):
    is_published: bool = False  # false = draft, true = published
    items: Optional[List[PlaylistItemCreateSimple]] = None  # Items to add to playlist


class PlaylistUpdate(BaseModel):
    name: Optional[str] = Field(None, min_length=1, max_length=255)
    description: Optional[str] = None
    default_duration: Optional[float] = Field(None, ge=1, le=3600)
    transition: Optional[str] = Field(None, pattern="^(fade|slide|none)$")
    loop: Optional[bool] = None
    is_published: Optional[bool] = None


class PlaylistResponse(BaseModel):
    id: str
    name: str
    description: Optional[str]
    default_duration: float
    transition: str
    loop: bool
    is_published: bool
    items_count: int
    total_duration: float  # in seconds
    used_in: int
    created_at: datetime
    updated_at: datetime

    class Config:
        from_attributes = True


class PlaylistDetailResponse(PlaylistResponse):
    items: List['PlaylistItemResponse']


# Add missing PlaylistListResponse
PlaylistListResponse = List[PlaylistResponse]


# ==================== Playlist Item ====================

class PlaylistItemBase(BaseModel):
    media_id: str = Field(..., min_length=1)
    duration: float = Field(..., ge=1, le=86400)  # seconds (max 24h)


class PlaylistItemCreate(PlaylistItemBase):
    pass


class PlaylistItemResponse(BaseModel):
    id: str
    playlist_id: str
    media_id: str
    name: str  # Media name
    duration: float
    order: int
    media_type: str  # 'video' or 'image'
    thumbnail_data: Optional[str] = None
    thumbnail_url: Optional[str] = None

    class Config:
        from_attributes = True


# Update forward references
PlaylistDetailResponse.model_rebuild()
