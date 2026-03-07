"""
Template schemas - request/response validation for Videotron template management.
"""
from pydantic import BaseModel, Field, ConfigDict
from typing import Optional, List
from datetime import datetime
import uuid


class TemplateBase(BaseModel):
    """Base template schema."""
    
    name: str = Field(..., min_length=1, max_length=500, description="Template name")
    description: Optional[str] = Field(None, description="Template description")
    layout_id: Optional[uuid.UUID] = Field(None, description="Associated layout UUID")
    thumbnail: Optional[str] = Field(None, description="Base64 encoded thumbnail or file path")
    category: Optional[str] = Field(None, max_length=100, description="Template category (e.g., lobby, retail, corporate)")


class TemplateCreate(TemplateBase):
    """Schema for template creation."""
    pass


class TemplateUpdate(BaseModel):
    """Schema for template update."""
    
    name: Optional[str] = Field(None, min_length=1, max_length=500)
    description: Optional[str] = None
    layout_id: Optional[uuid.UUID] = None
    thumbnail: Optional[str] = None
    category: Optional[str] = Field(None, max_length=100)


class TemplateResponse(BaseModel):
    """Schema for template response."""
    
    model_config = ConfigDict(from_attributes=True)
    
    id: uuid.UUID
    name: str
    description: Optional[str] = None
    layout_id: Optional[uuid.UUID] = None
    thumbnail: Optional[str] = None
    category: Optional[str] = None
    created_by: Optional[int] = None
    created_at: datetime
    updated_at: datetime


class TemplateListResponse(BaseModel):
    """Schema for template list response."""
    
    status: bool = True
    statusCode: int = 200
    message: str = "Success"
    templates: List[TemplateResponse]
    count: Optional[int] = None


class TemplateDetailResponse(BaseModel):
    """Schema for template detail response."""
    
    status: bool = True
    statusCode: int = 200
    message: str = "Success"
    template: TemplateResponse


class TemplateDeleteResponse(BaseModel):
    """Schema for template delete response."""
    
    success: bool = True
    message: str = "Template deleted successfully"


class TemplateDuplicateRequest(BaseModel):
    """Schema for template duplicate request."""
    
    name: Optional[str] = Field(None, min_length=1, max_length=500, description="New template name (optional)")
