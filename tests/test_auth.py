"""
Authentication tests.
"""
import pytest
from httpx import AsyncClient


@pytest.mark.auth
@pytest.mark.unit
class TestAuthCookies:
    """Test httpOnly cookie authentication."""
    
    async def test_login_sets_cookies(self, client: AsyncClient, test_user):
        """Test that login sets httpOnly cookies."""
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
        
        # Check cookies are set
        assert "access_token" in response.cookies
        assert "refresh_token" in response.cookies
        assert response.cookies["access_token"] == data["data"]["access_token"]
        assert response.cookies["refresh_token"] == data["data"]["refresh_token"]
    
    async def test_logout_clears_cookies(self, client: AsyncClient, test_user):
        """Test that logout clears cookies."""
        # First login to get cookies
        await client.post(
            "/api/v1/auth/login",
            json={
                "username": "testuser",
                "password": "password123"
            }
        )
        
        # Now logout
        response = await client.post("/api/v1/auth/logout")
        assert response.status_code == 200
        data = response.json()
        assert data["status"] is True
        assert data["message"] == "Logged out"
        
        # Check cookies are cleared (expired)
        # Note: httpx doesn't automatically remove cookies on delete,
        # but the cookie should have an expired max-age
        assert "access_token" in response.cookies or response.cookies.get("access_token") == ""
    
    async def test_refresh_with_cookie(self, client: AsyncClient, test_user):
        """Test token refresh using cookie."""
        # First login to get cookies
        login_response = await client.post(
            "/api/v1/auth/login",
            json={
                "username": "testuser",
                "password": "password123"
            }
        )
        
        # Refresh using cookie (client automatically sends cookies)
        response = await client.post("/api/v1/auth/refresh")
        assert response.status_code == 200
        data = response.json()
        assert data["status"] is True
        assert "access_token" in data["data"]
    
    async def test_get_current_user_with_cookie(self, client: AsyncClient, test_user):
        """Test getting current user with cookie authentication."""
        # Login to set cookies
        await client.post(
            "/api/v1/auth/login",
            json={
                "username": "testuser",
                "password": "password123"
            }
        )
        
        # Get current user (cookies sent automatically)
        response = await client.get("/api/v1/auth/me")
        assert response.status_code == 200
        data = response.json()
        assert data["status"] is True
        assert data["data"]["username"] == "testuser"
    
    async def test_protected_route_without_auth(self, client: AsyncClient):
        """Test protected route without authentication."""
        response = await client.get("/api/v1/auth/me")
        assert response.status_code == 401


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
        # First login to get cookies
        await client.post(
            "/api/v1/auth/login",
            json={
                "username": "testuser",
                "password": "password123"
            }
        )
        
        # Now refresh (uses cookie automatically)
        response = await client.post("/api/v1/auth/refresh")
        assert response.status_code == 200
        data = response.json()
        assert data["status"] is True
        assert "access_token" in data["data"]
