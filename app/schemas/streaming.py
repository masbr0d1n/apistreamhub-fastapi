"""
Streaming schemas - request/response validation.
"""
from pydantic import BaseModel, Field
from typing import Optional
from datetime import datetime


class StreamingStatus(BaseModel):
    """Streaming status data."""
    
    channel_id: int = Field(..., description="Channel ID")
    status: str = Field(..., description="Streaming status (on-air/off-air)")
    started_at: Optional[datetime] = Field(None, description="When streaming started")
    stopped_at: Optional[datetime] = Field(None, description="When streaming stopped")
    stream_url: Optional[str] = Field(None, description="Stream URL")
    
    class Config:
        from_attributes = True


class StreamingResponse(BaseModel):
    """Schema for streaming response."""
    
    status: bool = True
    statusCode: int = 200
    message: str = "Success"
    data: StreamingStatus
