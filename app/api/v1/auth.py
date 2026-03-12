"""
Authentication API routes.
"""
from fastapi import APIRouter, Depends, status, Request, Response, Body
from sqlalchemy.ext.asyncio import AsyncSession

from app.db.base import get_db
from app.schemas.auth import (
    UserCreate,
    UserLogin,
    UserResponse,
    AuthResponse,
    UserDetailResponse,
    RefreshTokenRequest
)
from app.services.auth_service import AuthService
from app.core.exceptions import StreamHubException, UnauthorizedException
from app.core.security import get_current_user, decode_access_token
from app.core.rate_limiter import limiter


router = APIRouter(prefix="/auth", tags=["authentication"])
auth_service = AuthService()


@router.post(
    "/register",
    response_model=UserDetailResponse,
    status_code=status.HTTP_201_CREATED,
    summary="Register a new user",
    description="Create a new user account with username, email, and password"
)
@limiter.limit("3/minute")
async def register(
    request: Request,
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
    description="Authenticate user and return JWT tokens with user data"
)
@limiter.limit("5/minute")
async def login(
    request: Request,
    user_login: UserLogin,
    response: Response,
    db: AsyncSession = Depends(get_db)
) -> AuthResponse:
    """
    Login user.
    
    Args:
        user_login: Login credentials
        response: FastAPI Response object for setting cookies
        db: Database session
        
    Returns:
        JWT tokens and user data
    """
    try:
        # Authenticate user
        user = await auth_service.authenticate(db, user_login.username, user_login.password)
        
        # Create tokens
        tokens = auth_service.create_tokens(user)
        
        # Set httpOnly cookies for cross-origin requests
        # IMPORTANT: SameSite=lax allows cookies in cross-origin contexts for same-site navigation
        response.set_cookie(
            key="access_token",
            value=tokens.access_token,
            httponly=True,
            secure=False,  # Set True in production with HTTPS
            samesite="lax",  # Required for cross-origin on localhost
            max_age=1800,  # 30 minutes
            path="/"
        )
        
        response.set_cookie(
            key="refresh_token",
            value=tokens.refresh_token,
            httponly=True,
            secure=False,  # Set True in production with HTTPS
            samesite="lax",  # Required for cross-origin on localhost
            max_age=2592000,  # 30 days
            path="/"
        )
        
        # Include user data in response
        return AuthResponse(
            status=True,
            statusCode=200,
            message="Login successful",
            data={
                "access_token": tokens.access_token,
                "refresh_token": tokens.refresh_token,
                "token_type": tokens.token_type,
                "expires_in": tokens.expires_in,
                "user": UserResponse.model_validate(user)
            }
        )
    except StreamHubException as e:
        raise e


@router.post(
    "/refresh",
    response_model=AuthResponse,
    summary="Refresh access token",
    description="Get a new access token using refresh token"
)
@limiter.limit("5/minute")
async def refresh_token(
    request: Request,
    db: AsyncSession = Depends(get_db),
    token_data: RefreshTokenRequest = None
) -> AuthResponse:
    """
    Refresh access token.

    Args:
        token_data: Refresh token from request body
        request: FastAPI Request object (for cookie access)
        db: Database session

    Returns:
        New access token with user data
    """
    # Try to get refresh_token from request body or cookie
    refresh_token = None
    if token_data:
        refresh_token = token_data.refresh_token
    if not refresh_token:
        refresh_token = request.cookies.get("refresh_token")

    if not refresh_token:
        raise UnauthorizedException("Refresh token required")

    try:
        # Decode refresh token
        payload = decode_access_token(refresh_token)

        # Get user
        user = await auth_service.get_by_id(db, int(payload["sub"]))

        # Create new tokens
        tokens = auth_service.create_tokens(user)

        # Return AuthTokenResponse (includes user data)
        return AuthResponse(
            status=True,
            statusCode=200,
            message="Token refreshed successfully",
            data={
                "access_token": tokens.access_token,
                "refresh_token": tokens.refresh_token,
                "token_type": tokens.token_type,
                "expires_in": tokens.expires_in,
                "user": UserResponse.model_validate(user)
            }
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
