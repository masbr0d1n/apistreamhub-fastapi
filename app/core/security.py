"""
Security utilities - password hashing and JWT.
"""
from datetime import datetime, timedelta
from typing import Optional
import bcrypt
from jose import JWTError, jwt
from fastapi import Depends, Request
from fastapi.security import OAuth2PasswordBearer
from sqlalchemy.ext.asyncio import AsyncSession

from app.config import settings
from app.core.exceptions import UnauthorizedException, StreamHubException
from app.db.base import get_db
from app.schemas.auth import UserResponse


# OAuth2 scheme for JWT authentication (fallback if cookie not present)
oauth2_scheme = OAuth2PasswordBearer(tokenUrl="/api/v1/auth/login")


# Dependency for protected routes
async def get_current_user(
    request: Request,
    db: AsyncSession = Depends(get_db)
) -> UserResponse:
    """
    Dependency to get current user from JWT token.
    
    This is used in protected routes like:
        @router.get("/protected-route")
        async def protected_route(current_user: UserResponse = Depends(get_current_user)):
            return {"message": f"Hello {current_user.username}"}
    
    Args:
        request: Request object (to get token from cookie or header)
        db: Database session
        
    Returns:
        Current authenticated user
        
    Raises:
        UnauthorizedException: If token is invalid or user not found
    """
    # Import here to avoid circular dependency
    from app.services.auth_service import AuthService
    
    # Try to get token from cookie first, then fall back to header
    token = request.cookies.get("access_token")
    if not token:
        # Fallback to Authorization header for backward compatibility
        try:
            token = await oauth2_scheme(request)
        except Exception:
            raise UnauthorizedException("Not authenticated")
    
    if not token:
        raise UnauthorizedException("Not authenticated")
    
    try:
        # Decode token
        payload = decode_access_token(token)
        
        # Get user
        auth_service = AuthService()
        user = await auth_service.get_by_id(db, int(payload["sub"]))
        
        return UserResponse.model_validate(user)
    except StreamHubException:
        raise UnauthorizedException("Invalid or expired token")
    except Exception:
        raise UnauthorizedException("Could not validate credentials")


def verify_password(plain_password: str, hashed_password: str) -> bool:
    """
    Verify a password against a hash.
    
    Args:
        plain_password: Plain text password
        hashed_password: Hashed password
        
    Returns:
        True if password matches
    """
    # Convert hash to bytes if needed
    if isinstance(hashed_password, str):
        hashed_password = hashed_password.encode('utf-8')
    
    # Bcrypt has a 72-byte limit
    password_bytes = plain_password.encode('utf-8')
    if len(password_bytes) > 72:
        password_bytes = password_bytes[:72]
        plain_password = password_bytes.decode('utf-8', errors='ignore')
    
    return bcrypt.checkpw(plain_password.encode('utf-8'), hashed_password)


def get_password_hash(password: str) -> str:
    """
    Hash a password.
    
    Args:
        password: Plain text password
        
    Returns:
        Hashed password
    """
    # Bcrypt has a 72-byte limit
    password_bytes = password.encode('utf-8')
    if len(password_bytes) > 72:
        password_bytes = password_bytes[:72]
    
    # Generate salt and hash
    salt = bcrypt.gensalt()
    hashed = bcrypt.hashpw(password_bytes, salt)
    
    # Return as string
    return hashed.decode('utf-8')


def create_access_token(data: dict, expires_delta: Optional[timedelta] = None) -> str:
    """
    Create JWT access token.
    
    Args:
        data: Data to encode in token
        expires_delta: Token expiration time
        
    Returns:
        Encoded JWT token
    """
    to_encode = data.copy()
    
    if expires_delta:
        expire = datetime.utcnow() + expires_delta
    else:
        expire = datetime.utcnow() + timedelta(
            minutes=settings.ACCESS_TOKEN_EXPIRE_MINUTES
        )
    
    to_encode.update({"exp": expire})
    encoded_jwt = jwt.encode(
        to_encode,
        settings.JWT_SECRET_KEY,
        algorithm=settings.JWT_ALGORITHM
    )
    
    return encoded_jwt


def decode_access_token(token: str) -> dict:
    """
    Decode and validate JWT token.
    
    Args:
        token: JWT token
        
    Returns:
        Decoded token payload
        
    Raises:
        UnauthorizedException: If token is invalid or expired
    """
    try:
        payload = jwt.decode(
            token,
            settings.JWT_SECRET_KEY,
            algorithms=[settings.JWT_ALGORITHM]
        )
        return payload
    except JWTError:
        raise UnauthorizedException("Invalid or expired token")
