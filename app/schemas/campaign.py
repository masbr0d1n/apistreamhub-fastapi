"""
Campaign schemas - request/response validation for Videotron campaign management.
"""
from pydantic import BaseModel, Field, ConfigDict
from typing import Optional, List, Any
from datetime import datetime
import uuid
from typing import Literal

CampaignStatusEnum = Literal["draft", "active", "paused", "completed"]


class CampaignBase(BaseModel):
    """Base campaign schema."""
    
    name: str = Field(..., min_length=1, max_length=500, description="Campaign name")
    description: Optional[str] = Field(None, description="Campaign description")
    screen_ids: List[uuid.UUID] = Field(default_factory=list, description="Array of screen UUIDs")
    layout_ids: List[uuid.UUID] = Field(default_factory=list, description="Array of layout UUIDs")
    start_date: Optional[datetime] = Field(None, description="Campaign start date")
    end_date: Optional[datetime] = Field(None, description="Campaign end date")


class CampaignCreate(CampaignBase):
    """Schema for campaign creation."""
    pass


class CampaignUpdate(BaseModel):
    """Schema for campaign update."""
    
    name: Optional[str] = Field(None, min_length=1, max_length=500)
    description: Optional[str] = None
    screen_ids: Optional[List[uuid.UUID]] = None
    layout_ids: Optional[List[uuid.UUID]] = None
    start_date: Optional[datetime] = None
    end_date: Optional[datetime] = None
    status: Optional[CampaignStatusEnum] = None


class CampaignResponse(BaseModel):
    """Schema for campaign response."""
    
    model_config = ConfigDict(from_attributes=True)
    
    id: uuid.UUID
    name: str
    description: Optional[str] = None
    screen_ids: List[uuid.UUID] = []
    layout_ids: List[uuid.UUID] = []
    status: str
    start_date: Optional[datetime] = None
    end_date: Optional[datetime] = None
    created_by: Optional[int] = None
    created_at: datetime
    updated_at: datetime


class CampaignListResponse(BaseModel):
    """Schema for campaign list response."""
    
    status: bool = True
    statusCode: int = 200
    message: str = "Success"
    campaigns: List[CampaignResponse]
    count: Optional[int] = None


class CampaignDetailResponse(BaseModel):
    """Schema for campaign detail response."""
    
    status: bool = True
    statusCode: int = 200
    message: str = "Success"
    campaign: CampaignResponse


class CampaignDeleteResponse(BaseModel):
    """Schema for campaign delete response."""
    
    success: bool = True
    message: str = "Campaign deleted successfully"


class CampaignActivateResponse(BaseModel):
    """Schema for campaign activate response."""
    
    success: bool = True
    message: str = "Campaign activated successfully"
    campaign: CampaignResponse


class CampaignDeactivateResponse(BaseModel):
    """Schema for campaign deactivate response."""
    
    success: bool = True
    message: str = "Campaign deactivated successfully"
    campaign: CampaignResponse
