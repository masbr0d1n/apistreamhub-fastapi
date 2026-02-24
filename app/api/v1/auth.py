"""
Authentication API routes.
"""
from fastapi import APIRouter, Depends, status
from fastapi.security import OAuth2PasswordBearer
from sqlalchemy.ext.asyncio import AsyncSession

from app.db.base import get_db
from app.schemas.auth import (
    UserCreate,
    UserLogin,
    UserResponse,
    Token,
    AuthResponse,
    UserDetailResponse
)
from app.services.auth_service import AuthService
from app.core.exceptions import StreamHubException
from app.core.security import decode_access_token


router = APIRouter(prefix="/auth", tags=["authentication"])
auth_service = AuthService()

# OAuth2 scheme for JWT authentication
oauth2_scheme = OAuth2PasswordBearer(tokenUrl="/api/v1/auth/login")


# Dependency for protected routes
async def get_current_user(
    token: str = Depends(oauth2_scheme),
    db: AsyncSession = Depends(get_db)
) -> UserResponse:
    """
    Dependency to get current user from JWT token.
    
    This is used in protected routes like:
        @router.get("/protected-route")
        async def protected_route(current_user: UserResponse = Depends(get_current_user)):
            return {"message": f"Hello {current_user.username}"}
    """
    try:
        # Decode token
        payload = decode_access_token(token)
        
        # Get user
        user = await auth_service.get_by_id(db, int(payload["sub"]))
        
        return UserResponse.model_validate(user)
    except StreamHubException:
        raise StreamHubException("Invalid token", status_code=401)


@router.post(
    "/register",
    response_model=UserDetailResponse,
    status_code=status.HTTP_201_CREATED,
    summary="Register a new user",
    description="Create a new user account with username, email, and password"
)
async def register(
    user_data: UserCreate,
    db: AsyncSession = Depends(get_db)
) -> UserDetailResponse:
    """
    Register a new user.
    
    Args:
        user_data: User registration data
        db: Database session
        
    Returns:
        Created user
    """
    try:
        user = await auth_service.register(db, user_data)
        
        return UserDetailResponse(
            status=True,
            statusCode=201,
            message="User registered successfully",
            data=UserResponse.model_validate(user)
        )
    except StreamHubException as e:
        raise e


@router.post(
    "/login",
    response_model=AuthResponse,
    summary="Login user",
    description="Authenticate user and return JWT tokens"
)
async def login(
    user_login: UserLogin,
    db: AsyncSession = Depends(get_db)
) -> AuthResponse:
    """
    Login user.
    
    Args:
        user_login: Login credentials
        db: Database session
        
    Returns:
        JWT tokens (access_token and refresh_token)
    """
    try:
        # Authenticate user
        user = await auth_service.authenticate(db, user_login.username, user_login.password)
        
        # Create tokens
        tokens = auth_service.create_tokens(user)
        
        return AuthResponse(
            status=True,
            statusCode=200,
            message="Login successful",
            data=tokens
        )
    except StreamHubException as e:
        raise e


@router.post(
    "/refresh",
    response_model=AuthResponse,
    summary="Refresh access token",
    description="Get a new access token using refresh token"
)
async def refresh_token(
    refresh_token: str,
    db: AsyncSession = Depends(get_db)
) -> AuthResponse:
    """
    Refresh access token.
    
    Args:
        refresh_token: Valid refresh token
        db: Database session
        
    Returns:
        New access token
    """
    try:
        # Decode refresh token
        payload = decode_access_token(refresh_token)
        
        # Get user
        user = await auth_service.get_by_id(db, int(payload["sub"]))
        
        # Create new access token
        tokens = auth_service.create_tokens(user)
        
        return AuthResponse(
            status=True,
            statusCode=200,
            message="Token refreshed successfully",
            data=tokens
        )
    except StreamHubException as e:
        raise e


@router.get(
    "/me",
    response_model=UserDetailResponse,
    summary="Get current user",
    description="Get current authenticated user information"
)
async def get_current_user_endpoint(
    current_user: UserResponse = Depends(get_current_user)
) -> UserDetailResponse:
    """
    Get current user.
    
    Args:
        current_user: Current authenticated user (from JWT token)
        
    Returns:
        Current user information
    """
    return UserDetailResponse(
        status=True,
        statusCode=200,
        message="Success",
        data=current_user
    )
