"""
Channel schemas - request/response validation.
"""
from datetime import datetime
from typing import Optional
from pydantic import BaseModel, Field, HttpUrl


class ChannelBase(BaseModel):
    """Base channel schema."""
    
    name: str = Field(..., min_length=1, max_length=255, description="Channel name")
    category: str = Field(..., pattern="^(sport|entertainment|kids|knowledge|gaming)$", description="Channel category")
    description: Optional[str] = Field(None, description="Channel description")


class ChannelCreate(ChannelBase):
    """Schema for creating a channel."""
    
    logo_url: Optional[str] = Field(None, max_length=500, description="Channel logo URL")


class ChannelUpdate(BaseModel):
    """Schema for updating a channel."""
    
    name: Optional[str] = Field(None, min_length=1, max_length=255)
    category: Optional[str] = Field(None, pattern="^(sport|entertainment|kids|knowledge|gaming)$")
    description: Optional[str] = None
    logo_url: Optional[str] = Field(None, max_length=500)


class ChannelResponse(ChannelBase):
    """Schema for channel response."""
    
    id: int
    logo_url: Optional[str] = None
    created_at: datetime
    updated_at: datetime
    
    class Config:
        from_attributes = True  # Pydantic v2 (ORM mode)


class ChannelListResponse(BaseModel):
    """Schema for list of channels response."""
    
    status: bool = True
    statusCode: int = 200
    message: str = "Success"
    data: list[ChannelResponse]
    count: int


class ChannelDetailResponse(BaseModel):
    """Schema for single channel response."""
    
    status: bool = True
    statusCode: int = 200
    message: str = "Success"
    data: ChannelResponse
