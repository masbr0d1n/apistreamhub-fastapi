"""
User management API routes.
"""
from fastapi import APIRouter, Depends, status
from sqlalchemy.ext.asyncio import AsyncSession

from app.db.base import get_db
from app.schemas.auth import (
    UserResponse,
    UserCreate,
    UserUpdate,
    UserDetailResponse,
    UserRole,
)
from app.services.auth_service import AuthService
from app.core.exceptions import StreamHubException, ForbiddenException
from app.core.security import get_current_user
from app.models.user import User as UserModel


router = APIRouter()
auth_service = AuthService()


@router.get(
    "",
    response_model=dict,
    summary="Get all users",
    description="Get list of all users (requires admin or superadmin role)"
)
async def get_all_users(
    current_user: UserModel = Depends(get_current_user),
    db: AsyncSession = Depends(get_db)
) -> dict:
    """
    Get all users.
    
    Args:
        current_user: Current authenticated user
        db: Database session
        
    Returns:
        List of users
    """
    # Check permissions - only admin and superadmin can view all users
    if current_user.role not in [UserRole.ADMIN, UserRole.SUPERADMIN]:
        raise ForbiddenException("Insufficient permissions")
    
    try:
        users = await auth_service.get_all_users(db)
        
        return {
            "status": True,
            "statusCode": 200,
            "message": "Users retrieved successfully",
            "data": [UserResponse.model_validate(u) for u in users]
        }
    except StreamHubException as e:
        raise e


@router.get(
    "/{user_id}",
    response_model=UserDetailResponse,
    summary="Get user by ID",
    description="Get detailed information about a specific user"
)
async def get_user(
    user_id: int,
    current_user: UserModel = Depends(get_current_user),
    db: AsyncSession = Depends(get_db)
) -> UserDetailResponse:
    """
    Get user by ID.
    
    Args:
        user_id: User ID
        current_user: Current authenticated user
        db: Database session
        
    Returns:
        User details
    """
    try:
        user = await auth_service.get_by_id(db, user_id)
        
        return UserDetailResponse(
            status=True,
            statusCode=200,
            message="User retrieved successfully",
            data=UserResponse.model_validate(user)
        )
    except StreamHubException as e:
        raise e


@router.put(
    "/{user_id}",
    response_model=UserDetailResponse,
    summary="Update user",
    description="Update user information (role, page access, etc.)"
)
async def update_user(
    user_id: int,
    user_data: UserUpdate,
    current_user: UserModel = Depends(get_current_user),
    db: AsyncSession = Depends(get_db)
) -> UserDetailResponse:
    """
    Update user.
    
    Args:
        user_id: ID of user to update
        user_data: Update data
        current_user: Current authenticated user
        db: Database session
        
    Returns:
        Updated user
    """
    try:
        user = await auth_service.update_user(db, user_id, user_data, current_user)
        
        return UserDetailResponse(
            status=True,
            statusCode=200,
            message="User updated successfully",
            data=UserResponse.model_validate(user)
        )
    except StreamHubException as e:
        raise e


@router.delete(
    "/{user_id}",
    response_model=dict,
    summary="Delete user",
    description="Delete a user account (superadmin can delete admin, admin can delete regular users)"
)
async def delete_user(
    user_id: int,
    current_user: UserModel = Depends(get_current_user),
    db: AsyncSession = Depends(get_db)
) -> dict:
    """
    Delete user.
    
    Args:
        user_id: ID of user to delete
        current_user: Current authenticated user
        db: Database session
        
    Returns:
        Success message
    """
    try:
        await auth_service.delete_user(db, user_id, current_user)
        
        return {
            "status": True,
            "statusCode": 200,
            "message": "User deleted successfully"
        }
    except StreamHubException as e:
        raise e
