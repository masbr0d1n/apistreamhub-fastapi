"""
Authentication schemas - request/response validation.
"""
from pydantic import BaseModel, EmailStr, Field
from typing import Optional
from enum import Enum


class UserRole(str, Enum):
    """User roles."""
    SUPERADMIN = "superadmin"
    ADMIN = "admin"
    USER = "user"


class UserBase(BaseModel):
    """Base user schema."""
    
    username: str = Field(..., min_length=3, max_length=100, description="Username")
    email: EmailStr = Field(..., description="Email address")
    full_name: str = Field(..., min_length=1, max_length=255, description="Full name")
    role: UserRole = Field(default=UserRole.USER, description="User role")


class UserCreate(UserBase):
    """Schema for user registration."""
    
    password: str = Field(..., min_length=6, max_length=100, description="Password")
    page_access: Optional[dict] = Field(None, description="Page access permissions")


class UserUpdate(BaseModel):
    """Schema for user update."""
    
    email: Optional[EmailStr] = None
    full_name: Optional[str] = None
    role: Optional[UserRole] = None
    page_access: Optional[dict] = None
    is_active: Optional[bool] = None
    password: Optional[str] = Field(None, min_length=6, max_length=100)


class UserLogin(BaseModel):
    """Schema for user login."""
    
    username: str = Field(..., description="Username or email")
    password: str = Field(..., description="Password")


class RefreshTokenRequest(BaseModel):
    """Schema for token refresh request."""
    
    refresh_token: str = Field(..., description="Valid refresh token")


class UserResponse(UserBase):
    """Schema for user response."""
    
    id: int
    is_active: bool
    is_admin: bool  # Deprecated, kept for compatibility
    role: UserRole
    page_access: Optional[dict] = None
    
    class Config:
        from_attributes = True


class Token(BaseModel):
    """Schema for JWT token response."""
    
    access_token: str
    refresh_token: str
    token_type: str = "bearer"
    expires_in: int  # seconds


class AuthTokenResponse(BaseModel):
    """Schema for authentication response with user data."""
    
    access_token: str
    refresh_token: str
    token_type: str = "bearer"
    expires_in: int  # seconds
    user: UserResponse


class TokenPayload(BaseModel):
    """Schema for token payload."""
    
    sub: int  # user ID
    username: str
    exp: int  # expiration timestamp


class AuthResponse(BaseModel):
    """Schema for authentication response."""
    
    status: bool = True
    statusCode: int = 200
    message: str = "Success"
    data: AuthTokenResponse


class UserDetailResponse(BaseModel):
    """Schema for user detail response."""
    
    status: bool = True
    statusCode: int = 200
    message: str = "Success"
    data: UserResponse
