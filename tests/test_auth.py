"""
Authentication tests.
"""
import pytest
from httpx import AsyncClient


@pytest.mark.auth
@pytest.mark.unit
class TestAuth:
    """Test authentication endpoints."""
    
    async def test_register_user(self, client: AsyncClient):
        """Test user registration."""
        response = await client.post(
            "/api/v1/auth/register",
            json={
                "username": "newuser",
                "email": "newuser@example.com",
                "full_name": "New User",
                "password": "password123"
            }
        )
        assert response.status_code == 201
        data = response.json()
        assert data["status"] is True
        assert data["statusCode"] == 201
        assert data["data"]["username"] == "newuser"
        assert data["data"]["email"] == "newuser@example.com"
        assert "id" in data["data"]
    
    async def test_register_duplicate_username(self, client: AsyncClient, test_user):
        """Test registration with duplicate username."""
        response = await client.post(
            "/api/v1/auth/register",
            json={
                "username": "testuser",
                "email": "different@example.com",
                "full_name": "Different User",
                "password": "password123"
            }
        )
        assert response.status_code == 409
        data = response.json()
        assert data["status"] is False
    
    async def test_register_duplicate_email(self, client: AsyncClient, test_user):
        """Test registration with duplicate email."""
        response = await client.post(
            "/api/v1/auth/register",
            json={
                "username": "different",
                "email": "test@example.com",
                "full_name": "Different User",
                "password": "password123"
            }
        )
        assert response.status_code == 409
        data = response.json()
        assert data["status"] is False
    
    async def test_login_success(self, client: AsyncClient, test_user):
        """Test successful login."""
        response = await client.post(
            "/api/v1/auth/login",
            json={
                "username": "testuser",
                "password": "password123"
            }
        )
        assert response.status_code == 200
        data = response.json()
        assert data["status"] is True
        assert "access_token" in data["data"]
        assert "refresh_token" in data["data"]
        assert data["data"]["token_type"] == "bearer"
    
    async def test_login_invalid_username(self, client: AsyncClient):
        """Test login with invalid username."""
        response = await client.post(
            "/api/v1/auth/login",
            json={
                "username": "invaliduser",
                "password": "password123"
            }
        )
        assert response.status_code == 401
        data = response.json()
        assert data["status"] is False
    
    async def test_login_invalid_password(self, client: AsyncClient, test_user):
        """Test login with invalid password."""
        response = await client.post(
            "/api/v1/auth/login",
            json={
                "username": "testuser",
                "password": "wrongpassword"
            }
        )
        assert response.status_code == 401
        data = response.json()
        assert data["status"] is False
    
    async def test_get_current_user(self, client: AsyncClient, auth_headers):
        """Test getting current user."""
        response = await client.get(
            "/api/v1/auth/me",
            headers=auth_headers
        )
        assert response.status_code == 200
        data = response.json()
        assert data["status"] is True
        assert data["data"]["username"] == "testuser"
    
    async def test_get_current_user_unauthorized(self, client: AsyncClient):
        """Test getting current user without token."""
        response = await client.get("/api/v1/auth/me")
        assert response.status_code == 401
    
    async def test_refresh_token(self, client: AsyncClient, test_user):
        """Test token refresh."""
        # First login to get refresh token
        response = await client.post(
            "/api/v1/auth/login",
            json={
                "username": "testuser",
                "password": "password123"
            }
        )
        refresh_token = response.json()["data"]["refresh_token"]
        
        # Now refresh
        response = await client.post(
            "/api/v1/auth/refresh",
            params={"refresh_token": refresh_token}
        )
        assert response.status_code == 200
        data = response.json()
        assert data["status"] is True
        assert "access_token" in data["data"]
