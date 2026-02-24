"""
Authentication schemas - request/response validation.
"""
from pydantic import BaseModel, EmailStr, Field


class UserBase(BaseModel):
    """Base user schema."""
    
    username: str = Field(..., min_length=3, max_length=100, description="Username")
    email: EmailStr = Field(..., description="Email address")
    full_name: str = Field(..., min_length=1, max_length=255, description="Full name")


class UserCreate(UserBase):
    """Schema for user registration."""
    
    password: str = Field(..., min_length=6, max_length=100, description="Password")


class UserLogin(BaseModel):
    """Schema for user login."""
    
    username: str = Field(..., description="Username or email")
    password: str = Field(..., description="Password")


class UserResponse(UserBase):
    """Schema for user response."""
    
    id: int
    is_active: bool
    is_admin: bool
    
    class Config:
        from_attributes = True


class Token(BaseModel):
    """Schema for JWT token response."""
    
    access_token: str
    refresh_token: str
    token_type: str = "bearer"
    expires_in: int  # seconds


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
    data: Token


class UserDetailResponse(BaseModel):
    """Schema for user detail response."""
    
    status: bool = True
    statusCode: int = 200
    message: str = "Success"
    data: UserResponse
