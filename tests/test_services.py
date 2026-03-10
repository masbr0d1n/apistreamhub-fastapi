"""
Service layer tests for StreamHub API.
Tests for auth_service, video_service, channel_service.
"""
import pytest
from datetime import datetime, timedelta
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select

from app.schemas.auth import UserCreate, UserLogin, UserUpdate
from app.schemas.video import VideoCreate, VideoUpdate
from app.schemas.channel import ChannelCreate, ChannelUpdate
from app.services.auth_service import AuthService
from app.services.channel_service import ChannelService
from app.core.security import verify_password, get_password_hash, create_access_token, decode_access_token
from app.models.channel import Channel
from app.core.exceptions import NotFoundException, ConflictException, UnauthorizedException


@pytest.mark.unit
@pytest.mark.service
class TestAuthService:
    """Test AuthService business logic."""
    
    async def test_register_user_success(self, test_db: AsyncSession):
        """Test successful user registration."""
        auth_service = AuthService()
        user_data = UserCreate(
            username="newuser",
            email="newuser@example.com",
            full_name="New User",
            password="SecurePass123!"
        )
        
        user = await auth_service.register(test_db, user_data)
        
        assert user is not None
        assert user.username == "newuser"
        assert user.email == "newuser@example.com"
        assert user.full_name == "New User"
        assert verify_password("SecurePass123!", user.hashed_password)
    
    async def test_register_duplicate_username(self, test_db: AsyncSession, test_user):
        """Test registration with duplicate username."""
        auth_service = AuthService()
        user_data = UserCreate(
            username="testuser",
            email="different@example.com",
            full_name="Different User",
            password="SecurePass123!"
        )
        
        with pytest.raises(ValueError) as exc_info:
            await auth_service.register(test_db, user_data)
        
        assert "Username already registered" in str(exc_info.value)
    
    async def test_register_duplicate_email(self, test_db: AsyncSession, test_user):
        """Test registration with duplicate email."""
        auth_service = AuthService()
        user_data = UserCreate(
            username="differentuser",
            email="test@example.com",
            full_name="Different User",
            password="SecurePass123!"
        )
        
        with pytest.raises(ValueError) as exc_info:
            await auth_service.register(test_db, user_data)
        
        assert "Email already registered" in str(exc_info.value)
    
    async def test_authenticate_user_success(self, test_db: AsyncSession, test_user):
        """Test successful user authentication."""
        auth_service = AuthService()
        
        user = await auth_service.authenticate(
            test_db, 
            "testuser", 
            "password123"
        )
        
        assert user is not None
        assert user.username == "testuser"
    
    async def test_authenticate_user_wrong_password(self, test_db: AsyncSession, test_user):
        """Test authentication with wrong password."""
        auth_service = AuthService()
        
        with pytest.raises(UnauthorizedException):
            await auth_service.authenticate(
                test_db, 
                "testuser", 
                "wrongpassword"
            )
    
    async def test_authenticate_user_nonexistent(self, test_db: AsyncSession):
        """Test authentication with non-existent user."""
        auth_service = AuthService()
        
        with pytest.raises(UnauthorizedException):
            await auth_service.authenticate(
                test_db, 
                "nonexistentuser", 
                "password123"
            )
    
    async def test_create_access_token(self, test_user):
        """Test access token creation."""
        token = create_access_token(
            data={"sub": test_user.username}
        )
        
        assert token is not None
        assert isinstance(token, str)
        assert len(token) > 0
    
    async def test_decode_token_valid(self, test_user):
        """Test decoding a valid token."""
        token = create_access_token(
            data={"sub": test_user.username}
        )
        
        payload = decode_access_token(token)
        
        assert payload is not None
        assert payload["sub"] == test_user.username
    
    async def test_decode_token_expired(self, test_user):
        """Test decoding an expired token."""
        token = create_access_token(
            data={"sub": test_user.username},
            expires_delta=timedelta(seconds=-1)
        )
        
        payload = decode_access_token(token)
        
        assert payload is None
    
    async def test_decode_token_invalid(self):
        """Test decoding an invalid token."""
        payload = decode_access_token("invalid.token.here")
        
        assert payload is None
    
    async def test_password_hashing(self):
        """Test password hashing and verification."""
        password = "TestPassword123!"
        hashed = get_password_hash(password)
        
        assert hashed != password
        assert verify_password(password, hashed)
        assert not verify_password("wrongpassword", hashed)


@pytest.mark.unit
@pytest.mark.service
class TestChannelService:
    """Test ChannelService business logic."""
    
    async def test_create_channel_success(self, test_db: AsyncSession):
        """Test successful channel creation."""
        channel_service = ChannelService()
        channel_data = ChannelCreate(
            name="New Test Channel",
            category="gaming",
            description="A gaming channel"
        )
        
        channel = await channel_service.create(test_db, channel_data)
        
        assert channel is not None
        assert channel.name == "New Test Channel"
        assert channel.category == "gaming"
    
    async def test_create_duplicate_channel(self, test_db: AsyncSession, test_channel):
        """Test creating duplicate channel."""
        channel_service = ChannelService()
        channel_data = ChannelCreate(
            name="Test Channel",
            category="gaming"
        )
        
        with pytest.raises(ConflictException) as exc_info:
            await channel_service.create(test_db, channel_data)
        
        assert "already exists" in str(exc_info.value)
    
    async def test_get_by_id(self, test_db: AsyncSession, test_channel):
        """Test getting channel by ID."""
        channel_service = ChannelService()
        
        channel = await channel_service.get_by_id(test_db, test_channel.id)
        
        assert channel is not None
        assert channel.id == test_channel.id
        assert channel.name == "Test Channel"
    
    async def test_get_by_id_not_found(self, test_db: AsyncSession):
        """Test getting non-existent channel by ID."""
        channel_service = ChannelService()
        
        with pytest.raises(NotFoundException):
            await channel_service.get_by_id(test_db, 99999)
    
    async def test_get_by_name(self, test_db: AsyncSession, test_channel):
        """Test getting channel by name."""
        channel_service = ChannelService()
        
        channel = await channel_service.get_by_name(test_db, "Test Channel")
        
        assert channel is not None
        assert channel.name == "Test Channel"
    
    async def test_get_by_name_not_found(self, test_db: AsyncSession):
        """Test getting non-existent channel by name."""
        channel_service = ChannelService()
        
        channel = await channel_service.get_by_name(test_db, "NonExistent")
        
        assert channel is None
    
    async def test_get_all(self, test_db: AsyncSession):
        """Test listing all channels."""
        channel_service = ChannelService()
        
        # Create multiple channels
        for i in range(5):
            channel_data = ChannelCreate(
                name=f"Channel Test {i}",
                category="gaming",
                description=f"Test channel {i}"
            )
            await channel_service.create(test_db, channel_data)
        
        channels = await channel_service.get_all(test_db, skip=0, limit=10)
        
        assert len(channels) >= 5
    
    async def test_update_channel(self, test_db: AsyncSession, test_channel):
        """Test updating channel."""
        channel_service = ChannelService()
        
        update_data = ChannelUpdate(
            name="Updated Channel Name",
            description="Updated description"
        )
        
        updated = await channel_service.update(test_db, test_channel.id, update_data)
        
        assert updated is not None
        assert updated.name == "Updated Channel Name"
    
    async def test_update_channel_not_found(self, test_db: AsyncSession):
        """Test updating non-existent channel."""
        channel_service = ChannelService()
        
        update_data = ChannelUpdate(name="New Name")
        
        with pytest.raises(NotFoundException):
            await channel_service.update(test_db, 99999, update_data)
    
    async def test_delete_channel(self, test_db: AsyncSession):
        """Test deleting channel."""
        channel_service = ChannelService()
        
        # Create a channel
        channel_data = ChannelCreate(
            name="Delete Me Channel",
            category="gaming",
            description="To be deleted"
        )
        channel = await channel_service.create(test_db, channel_data)
        
        # Delete it
        success = await channel_service.delete(test_db, channel.id)
        
        assert success is True
        
        # Verify it's deleted
        with pytest.raises(NotFoundException):
            await channel_service.get_by_id(test_db, channel.id)
    
    async def test_delete_channel_not_found(self, test_db: AsyncSession):
        """Test deleting non-existent channel."""
        channel_service = ChannelService()
        
        with pytest.raises(NotFoundException):
            await channel_service.delete(test_db, 99999)


@pytest.mark.unit
@pytest.mark.security
class TestSecurityModule:
    """Test security module functions."""
    
    def test_password_hash_uniqueness(self):
        """Test that same password produces different hashes."""
        password = "SamePassword123!"
        hash1 = get_password_hash(password)
        hash2 = get_password_hash(password)
        
        # Hashes should be different due to salt
        assert hash1 != hash2
        # But both should verify
        assert verify_password(password, hash1)
        assert verify_password(password, hash2)
    
    def test_verify_password_case_sensitive(self):
        """Test password verification is case sensitive."""
        password = "Password123!"
        hashed = get_password_hash(password)
        
        assert verify_password(password, hashed)
        assert not verify_password("password123!", hashed)
        assert not verify_password("PASSWORD123!", hashed)
    
    def test_hash_different_passwords(self):
        """Test different passwords produce different hashes."""
        hash1 = get_password_hash("Password1!")
        hash2 = get_password_hash("Password2!")
        
        assert hash1 != hash2


@pytest.mark.unit
@pytest.mark.exceptions
class TestExceptions:
    """Test custom exceptions."""
    
    def test_not_found_exception(self):
        """Test NotFoundException."""
        exc = NotFoundException("Resource not found")
        
        assert str(exc) == "Resource not found"
        assert exc.message == "Resource not found"
    
    def test_conflict_exception(self):
        """Test ConflictException."""
        exc = ConflictException("Resource already exists")
        
        assert str(exc) == "Resource already exists"
        assert exc.message == "Resource already exists"
    
    def test_exception_status_codes(self):
        """Test exception status codes."""
        not_found = NotFoundException("Not found")
        conflict = ConflictException("Conflict")
        
        assert not_found.status_code == 404
        assert conflict.status_code == 409
