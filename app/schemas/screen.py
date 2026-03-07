"""
Screen schemas - request/response validation for Videotron device management.
"""
from pydantic import BaseModel, Field, ConfigDict
from typing import Optional, List
from datetime import datetime
from enum import Enum
import uuid


class ScreenStatusEnum(str, Enum):
    """Screen status enumeration for API."""
    ONLINE = "online"
    OFFLINE = "offline"
    MAINTENANCE = "maintenance"


class ScreenBase(BaseModel):
    """Base screen schema."""
    
    name: str = Field(..., min_length=1, max_length=500, description="Screen name")
    device_id: str = Field(..., min_length=1, max_length=255, description="Unique device identifier")
    location: Optional[str] = Field(None, max_length=500, description="Physical location")
    resolution: Optional[str] = Field(None, max_length=50, description="Screen resolution (e.g., 1920x1080)")


class ScreenCreate(ScreenBase):
    """Schema for screen creation."""
    pass


class ScreenUpdate(BaseModel):
    """Schema for screen update."""
    
    name: Optional[str] = Field(None, min_length=1, max_length=500)
    location: Optional[str] = Field(None, max_length=500)
    resolution: Optional[str] = Field(None, max_length=50)
    status: Optional[ScreenStatusEnum] = None


class ScreenHeartbeat(BaseModel):
    """Schema for screen heartbeat update."""
    
    status: ScreenStatusEnum = Field(..., description="Screen status (online/offline)")


class ScreenResponse(BaseModel):
    """Schema for screen response."""
    
    model_config = ConfigDict(from_attributes=True)
    
    id: uuid.UUID
    device_id: str
    name: str
    location: Optional[str] = None
    resolution: Optional[str] = None
    status: ScreenStatusEnum
    last_heartbeat: Optional[datetime] = None
    api_key: Optional[str] = None
    created_at: datetime
    updated_at: datetime


class ScreenListResponse(BaseModel):
    """Schema for screen list response."""
    
    status: bool = True
    statusCode: int = 200
    message: str = "Success"
    screens: List[ScreenResponse]
    count: Optional[int] = None


class ScreenDetailResponse(BaseModel):
    """Schema for screen detail response."""
    
    status: bool = True
    statusCode: int = 200
    message: str = "Success"
    screen: ScreenResponse


class ScreenDeleteResponse(BaseModel):
    """Schema for screen delete response."""
    
    success: bool = True
    message: str = "Screen deleted successfully"


class ScreenHeartbeatResponse(BaseModel):
    """Schema for screen heartbeat response."""
    
    success: bool = True
    last_heartbeat: datetime
    message: str = "Heartbeat updated successfully"


# Screen Group Schemas

class ScreenGroupBase(BaseModel):
    """Base screen group schema."""
    
    name: str = Field(..., min_length=1, max_length=500, description="Group name")
    screen_ids: List[str] = Field(default_factory=list, description="List of screen IDs")


class ScreenGroupCreate(ScreenGroupBase):
    """Schema for screen group creation."""
    pass


class ScreenGroupResponse(BaseModel):
    """Schema for screen group response."""
    
    model_config = ConfigDict(from_attributes=True)
    
    id: uuid.UUID
    name: str
    screen_ids: List[uuid.UUID] = []
    created_at: datetime


class ScreenGroupListResponse(BaseModel):
    """Schema for screen group list response."""
    
    status: bool = True
    statusCode: int = 200
    message: str = "Success"
    groups: List[ScreenGroupResponse]
    count: Optional[int] = None


class ScreenGroupDetailResponse(BaseModel):
    """Schema for screen group detail response."""
    
    status: bool = True
    statusCode: int = 200
    message: str = "Success"
    group: ScreenGroupResponse


class ScreenGroupDeleteResponse(BaseModel):
    """Schema for screen group delete response."""
    
    success: bool = True
    message: str = "Screen group deleted successfully"
