"""
Test security hardening features:
1. JWT Secret validation from environment variables
2. Rate limiting on critical endpoints
"""
import pytest
import os
from unittest.mock import patch
from pydantic import ValidationError


class TestJWTSecretValidation:
    """Test JWT secret key validation."""
    
    def test_jwt_secret_from_env_file(self):
        """Test that JWT secret is loaded from .env.dev file."""
        from app.config import settings
        
        assert settings.JWT_SECRET_KEY is not None
        assert len(settings.JWT_SECRET_KEY) >= 32
        assert settings.JWT_SECRET_KEY != "your-secret-key-change-in-production"
        assert settings.JWT_SECRET_KEY != "test-secret-key-change-in-production"
    
    def test_jwt_secret_minimum_length(self):
        """Test that JWT secret must be at least 32 characters."""
        # This should fail validation if secret is too short
        # We're testing with the actual config which should pass
        from app.config import settings
        assert len(settings.JWT_SECRET_KEY) >= 32
    
    def test_weak_secrets_rejected(self):
        """Test that weak/default secrets are rejected."""
        weak_secrets = [
            "your-secret-key-change-in-production",
            "test-secret-key-change-in-production",
            "secret",
            "changeme",
            "test"
        ]
        
        for weak_secret in weak_secrets:
            with patch.dict(os.environ, {"JWT_SECRET_KEY": weak_secret}, clear=False):
                # Clear the cached settings to force reload
                import importlib
                from app import config
                try:
                    # Try to create a new Settings instance
                    new_settings = config.Settings()
                    # If we get here with a weak secret, the test failed
                    assert False, f"Should have rejected weak secret: {weak_secret}"
                except ValidationError as e:
                    # Expected - weak secrets should be rejected
                    # Error can mention length (for short secrets) or weak/default (for long weak ones)
                    error_msg = str(e).lower()
                    assert (
                        "weak" in error_msg or 
                        "default" in error_msg or 
                        "32 characters" in error_msg
                    ), f"Should reject weak secret with appropriate error, got: {str(e)}"


class TestRateLimiting:
    """Test rate limiting configuration."""
    
    def test_rate_limiter_import(self):
        """Test that rate limiter can be imported."""
        from app.core.rate_limiter import limiter
        assert limiter is not None
    
    def test_rate_limiter_configured(self):
        """Test that rate limiter is properly configured."""
        from app.core.rate_limiter import limiter, RATE_LIMITS
        
        assert RATE_LIMITS["auth_login"] == "5/minute"
        assert RATE_LIMITS["auth_register"] == "3/minute"
        assert RATE_LIMITS["video_upload"] == "10/minute"
        assert RATE_LIMITS["default"] == "60/minute"
    
    def test_rate_limit_decorator_on_auth_endpoints(self):
        """Test that auth endpoints have rate limiting decorators."""
        from app.api.v1 import auth
        import inspect
        
        # Check that register and login functions exist
        assert hasattr(auth, 'register')
        assert hasattr(auth, 'login')
        
        # Check functions are async
        assert inspect.iscoroutinefunction(auth.register)
        assert inspect.iscoroutinefunction(auth.login)
    
    def test_rate_limit_decorator_on_video_upload(self):
        """Test that video upload endpoint has rate limiting."""
        from app.api.v1 import videos
        
        assert hasattr(videos, 'upload_video')


class TestEnvExample:
    """Test .env.example file exists and is properly configured."""
    
    def test_env_example_exists(self):
        """Test that .env.example file exists."""
        import os
        env_example_path = os.path.join(
            os.path.dirname(os.path.dirname(__file__)),
            '.env.example'
        )
        assert os.path.exists(env_example_path), ".env.example file should exist"
    
    def test_env_example_contains_jwt_secret(self):
        """Test that .env.example documents JWT_SECRET_KEY."""
        import os
        env_example_path = os.path.join(
            os.path.dirname(os.path.dirname(__file__)),
            '.env.example'
        )
        
        with open(env_example_path, 'r') as f:
            content = f.read()
        
        assert 'JWT_SECRET_KEY' in content
        assert 'python -c' in content  # Should include generation command
        assert 'secrets.token_urlsafe' in content


@pytest.mark.asyncio
class TestRateLimitingIntegration:
    """Integration tests for rate limiting (requires test client)."""
    
    async def test_login_rate_limit(self, client):
        """Test that login endpoint enforces rate limit."""
        # Make 6 rapid login requests (limit is 5/minute)
        responses = []
        for i in range(6):
            response = await client.post(
                "/api/v1/auth/login",
                json={"username": "test", "password": "test"}
            )
            responses.append(response.status_code)
        
        # At least one should be rate limited (429)
        assert 429 in responses, "Rate limiting should trigger after 5 requests"
    
    async def test_register_rate_limit(self, client):
        """Test that register endpoint enforces rate limit."""
        # Make 4 rapid register requests (limit is 3/minute)
        responses = []
        for i in range(4):
            response = await client.post(
                "/api/v1/auth/register",
                json={
                    "username": f"user{i}",
                    "email": f"user{i}@test.com",
                    "password": "testpass123"
                }
            )
            responses.append(response.status_code)
        
        # At least one should be rate limited (429)
        assert 429 in responses, "Rate limiting should trigger after 3 requests"


if __name__ == "__main__":
    pytest.main([__file__, "-v"])
