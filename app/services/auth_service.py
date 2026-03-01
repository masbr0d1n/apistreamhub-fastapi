"""
Authentication service - business logic for auth operations.
"""
from datetime import datetime, timedelta
from typing import Optional
from sqlalchemy import select, delete
from sqlalchemy.ext.asyncio import AsyncSession

from app.models.user import User, UserRole
from app.schemas.auth import UserCreate, UserUpdate, Token
from app.core.security import verify_password, get_password_hash, create_access_token
from app.core.exceptions import UnauthorizedException, ConflictException, ForbiddenException


class AuthService:
    """Service for authentication operations."""
    
    async def register(self, db: AsyncSession, user_data: UserCreate) -> User:
        """
        Register a new user.
        
        Args:
            db: Database session
            user_data: User registration data
            
        Returns:
            Created user
            
        Raises:
            ConflictException: If username or email already exists
        """
        # Check if username exists
        result = await db.execute(
            select(User).where(User.username == user_data.username)
        )
        if result.scalar_one_or_none():
            raise ConflictException(f"Username '{user_data.username}' already exists")
        
        # Check if email exists
        result = await db.execute(
            select(User).where(User.email == user_data.email)
        )
        if result.scalar_one_or_none():
            raise ConflictException(f"Email '{user_data.email}' already exists")
        
        # Create new user with role
        hashed_password = get_password_hash(user_data.password)
        user = User(
            username=user_data.username,
            email=user_data.email,
            full_name=user_data.full_name,
            hashed_password=hashed_password,
            role=user_data.role if hasattr(user_data, 'role') else UserRole.USER,
            page_access=getattr(user_data, 'page_access', None)
        )
        
        # Set is_admin based on role for compatibility
        user.is_admin = user.role in [UserRole.ADMIN, UserRole.SUPERADMIN]
        
        db.add(user)
        await db.commit()
        await db.refresh(user)
        
        return user
    
    async def update_user(self, db: AsyncSession, user_id: int, user_data: UserUpdate, current_user: User) -> User:
        """
        Update user data.
        
        Args:
            db: Database session
            user_id: ID of user to update
            user_data: Update data
            current_user: User performing the update
            
        Returns:
            Updated user
            
        Raises:
            UnauthorizedException: If user not found
            ForbiddenException: If insufficient permissions
        """
        result = await db.execute(
            select(User).where(User.id == user_id)
        )
        user = result.scalar_one_or_none()
        
        if not user:
            raise UnauthorizedException("User not found")
        
        # Check permissions
        if not current_user.can_manage_user(user.role):
            raise ForbiddenException("You don't have permission to manage this user")
        
        # Update fields
        if user_data.email:
            user.email = user_data.email
        if user_data.full_name:
            user.full_name = user_data.full_name
        if user_data.role:
            user.role = user_data.role
            user.is_admin = user.role in [UserRole.ADMIN, UserRole.SUPERADMIN]
        if user_data.page_access is not None:
            user.page_access = user_data.page_access
        if user_data.is_active is not None:
            user.is_active = user_data.is_active
        if user_data.password:
            user.hashed_password = get_password_hash(user_data.password)
        
        await db.commit()
        await db.refresh(user)
        
        return user
    
    async def delete_user(self, db: AsyncSession, user_id: int, current_user: User) -> bool:
        """
        Delete a user.
        
        Args:
            db: Database session
            user_id: ID of user to delete
            current_user: User performing the deletion
            
        Returns:
            True if deleted
            
        Raises:
            UnauthorizedException: If user not found
            ForbiddenException: If insufficient permissions or trying to delete self
        """
        # Can't delete yourself
        if user_id == current_user.id:
            raise ForbiddenException("Cannot delete your own account")
        
        result = await db.execute(
            select(User).where(User.id == user_id)
        )
        user = result.scalar_one_or_none()
        
        if not user:
            raise UnauthorizedException("User not found")
        
        # Check permissions using role directly (current_user is Pydantic model)
        # Superadmin can delete anyone except themselves
        # Admin can only delete regular users
        if current_user.role != 'superadmin':
            if current_user.role == 'admin' and user.role != 'user':
                raise ForbiddenException("Admins can only delete regular users")
            elif current_user.role == 'user':
                raise ForbiddenException("Users cannot delete other users")
        
        await db.execute(
            delete(User).where(User.id == user_id)
        )
        await db.commit()
        
        return True
    
    async def get_all_users(self, db: AsyncSession) -> list[User]:
        """
        Get all users.
        
        Args:
            db: Database session
            
        Returns:
            List of users
        """
        result = await db.execute(
            select(User).order_by(User.created_at.desc())
        )
        return list(result.scalars().all())
    
    async def authenticate(self, db: AsyncSession, username: str, password: str) -> User:
        """
        Authenticate user with username/email and password.
        
        Args:
            db: Database session
            username: Username or email
            password: Plain text password
            
        Returns:
            Authenticated user
            
        Raises:
            UnauthorizedException: If authentication fails
        """
        # Try to find user by username or email
        result = await db.execute(
            select(User).where(
                (User.username == username) | (User.email == username)
            )
        )
        user = result.scalar_one_or_none()
        
        if not user:
            raise UnauthorizedException("Invalid username or password")
        
        if not verify_password(password, user.hashed_password):
            raise UnauthorizedException("Invalid username or password")
        
        if not user.is_active:
            raise UnauthorizedException("User account is inactive")
        
        # Update last login
        user.last_login = datetime.utcnow()
        await db.commit()
        
        return user
    
    async def get_by_id(self, db: AsyncSession, user_id: int) -> User:
        """
        Get user by ID.
        
        Args:
            db: Database session
            user_id: User ID
            
        Returns:
            User object
            
        Raises:
            UnauthorizedException: If user not found
        """
        result = await db.execute(
            select(User).where(User.id == user_id)
        )
        user = result.scalar_one_or_none()
        
        if not user:
            raise UnauthorizedException("User not found")
        
        return user
    
    def create_tokens(self, user: User) -> Token:
        """
        Create access and refresh tokens for user.
        
        Args:
            user: User object
            
        Returns:
            Token object with access_token and refresh_token
        """
        # Create access token
        access_token_expires = timedelta(minutes=60 * 24 * 3)  # 3 days
        access_token = create_access_token(
            data={"sub": str(user.id), "username": user.username},
            expires_delta=access_token_expires
        )
        
        # Create refresh token (longer expiration)
        refresh_token_expires = timedelta(days=30)
        refresh_token = create_access_token(
            data={"sub": str(user.id), "username": user.username},
            expires_delta=refresh_token_expires
        )
        
        # Calculate expiration in seconds
        expires_in = int(access_token_expires.total_seconds())
        
        return Token(
            access_token=access_token,
            refresh_token=refresh_token,
            token_type="bearer",
            expires_in=expires_in
        )
