"""
Role Preset schemas - request/response validation
"""
from pydantic import BaseModel, Field


class RolePresetBase(BaseModel):
    """Base role preset schema."""
    name: str = Field(..., min_length=1, max_length=100, description="Preset name")
    description: str = Field(None, max_length=500, description="Preset description")
    page_access: dict = Field(..., description="Page access configuration")


class RolePresetCreate(RolePresetBase):
    """Schema for creating role preset."""
    pass


class RolePresetUpdate(BaseModel):
    """Schema for updating role preset."""
    name: str = Field(None, min_length=1, max_length=100)
    description: str = Field(None, max_length=500)
    page_access: dict = None
    is_active: bool = None


class RolePresetResponse(RolePresetBase):
    """Schema for role preset response."""
    id: int
    is_system: bool
    is_active: bool
    created_at: str
    
    class Config:
        from_attributes = True


class RolePresetListResponse(BaseModel):
    """Schema for role preset list response."""
    status: bool = True
    statusCode: int = 200
    message: str = "Success"
    data: list[RolePresetResponse]
