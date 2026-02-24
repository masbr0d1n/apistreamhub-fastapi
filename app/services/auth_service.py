"""
Authentication service - business logic for auth operations.
"""
from datetime import datetime, timedelta
from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from app.models.user import User
from app.schemas.auth import UserCreate, Token
from app.core.security import verify_password, get_password_hash, create_access_token
from app.core.exceptions import UnauthorizedException, ConflictException


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
        
        # Create new user
        hashed_password = get_password_hash(user_data.password)
        user = User(
            username=user_data.username,
            email=user_data.email,
            full_name=user_data.full_name,
            hashed_password=hashed_password
        )
        
        db.add(user)
        await db.commit()
        await db.refresh(user)
        
        return user
    
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
