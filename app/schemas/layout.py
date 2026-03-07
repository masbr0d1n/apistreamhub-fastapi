"""
Layout schemas - request/response validation for Videotron layout management.
"""
from pydantic import BaseModel, Field, ConfigDict
from typing import Optional, List, Any
from datetime import datetime
import uuid


class CanvasConfig(BaseModel):
    """Canvas configuration schema."""
    
    width: Optional[int] = Field(None, description="Canvas width in pixels")
    height: Optional[int] = Field(None, description="Canvas height in pixels")
    orientation: Optional[str] = Field(None, description="Canvas orientation (landscape/portrait)")


class LayerBase(BaseModel):
    """Base layer schema."""
    
    type: str = Field(..., description="Layer type (video, image, text, etc.)")
    position: Optional[dict] = Field(None, description="Position {x, y}")
    size: Optional[dict] = Field(None, description="Size {width, height}")
    properties: Optional[dict] = Field(None, description="Layer-specific properties")


class LayoutBase(BaseModel):
    """Base layout schema."""
    
    name: str = Field(..., min_length=1, max_length=500, description="Layout name")
    canvas_config: Optional[dict] = Field(None, description="Canvas configuration")
    layers: Optional[List[dict]] = Field(default_factory=list, description="Array of layer objects")


class LayoutCreate(LayoutBase):
    """Schema for layout creation."""
    pass


class LayoutUpdate(BaseModel):
    """Schema for layout update."""
    
    name: Optional[str] = Field(None, min_length=1, max_length=500)
    canvas_config: Optional[dict] = None
    layers: Optional[List[dict]] = None


class LayoutResponse(BaseModel):
    """Schema for layout response."""
    
    model_config = ConfigDict(from_attributes=True)
    
    id: uuid.UUID
    name: str
    canvas_config: Optional[dict] = None
    layers: Optional[List[dict]] = None
    created_by: Optional[int] = None
    created_at: datetime
    updated_at: datetime


class LayoutListResponse(BaseModel):
    """Schema for layout list response."""
    
    status: bool = True
    statusCode: int = 200
    message: str = "Success"
    layouts: List[LayoutResponse]
    count: Optional[int] = None


class LayoutDetailResponse(BaseModel):
    """Schema for layout detail response."""
    
    status: bool = True
    statusCode: int = 200
    message: str = "Success"
    layout: LayoutResponse


class LayoutDeleteResponse(BaseModel):
    """Schema for layout delete response."""
    
    success: bool = True
    message: str = "Layout deleted successfully"


class LayoutDuplicateRequest(BaseModel):
    """Schema for layout duplicate request."""
    
    name: Optional[str] = Field(None, min_length=1, max_length=500, description="New layout name (optional)")
