"""
Application configuration using Pydantic Settings.
"""
from typing import List
from pydantic import Field, field_validator
from pydantic_settings import BaseSettings, SettingsConfigDict


class Settings(BaseSettings):
    """Application settings."""
    
    model_config = SettingsConfigDict(
        env_file=".env.dev",
        env_file_encoding="utf-8",
        case_sensitive=False,
        extra="ignore"
    )
    
    # Application
    APP_NAME: str = "StreamHub API"
    APP_VERSION: str = "0.1.0"
    DEBUG: bool = True
    
    # Server
    HOST: str = "0.0.0.0"
    PORT: int = 8000
    
    # Database
    DATABASE_URL: str = Field(
        default="postgresql+asyncpg://postgres:postgres@apistreamhub-db:5432/apistreamhub",
        description="PostgreSQL connection string. Format: postgresql+asyncpg://user:password@host:port/database"
    )
    
    # JWT
    JWT_SECRET_KEY: str = Field(
        ...,
        description="JWT secret key - MUST be set in production. Generate with: python -c 'import secrets; print(secrets.token_urlsafe(32))'"
    )
    JWT_ALGORITHM: str = "HS256"
    ACCESS_TOKEN_EXPIRE_MINUTES: int = 60 * 24 * 3  # 3 days
    REFRESH_TOKEN_EXPIRE_DAYS: int = 30
    
    # CORS
    CORS_ORIGINS: str = Field(
        default="http://localhost:3000,http://localhost:3001,http://localhost:3002,http://localhost:3003,http://localhost:9000,http://localhost:3300,http://100.74.116.116:3002,https://streamhub.uzone.id,https://api-streamhub.uzone.id",
        description="Comma-separated list of allowed CORS origins. Localhost defaults included for development."
    )
    
    # File Upload
    UPLOAD_DIR: str = "uploads/"
    MAX_UPLOAD_SIZE: int = 10 * 1024 * 1024  # 10MB
    
    # Telegram
    TELEGRAM_BOT_TOKEN: str = ""
    TELEGRAM_CHAT_ID: str = ""
    
    # Streaming
    RTMP_STREAM_HOST: str = Field(
        default="localhost",
        description="RTMP server host for streaming URLs"
    )
    RTMP_STREAM_PORT: int = Field(
        default=1935,
        description="RTMP server port (default: 1935)"
    )
    
    @property
    def cors_origins_list(self) -> List[str]:
        """Get CORS origins as a list of strings."""
        return [origin.strip() for origin in self.CORS_ORIGINS.split(",") if origin.strip()]
    
    @field_validator("JWT_SECRET_KEY", mode="after")
    @classmethod
    def validate_jwt_secret(cls, v):
        """Validate JWT secret is strong enough for production."""
        if not v:
            raise ValueError("JWT_SECRET_KEY cannot be empty")
        
        # Check minimum length (32 characters recommended)
        if len(v) < 32:
            raise ValueError(
                f"JWT_SECRET_KEY must be at least 32 characters long. "
                f"Current length: {len(v)}. "
                f"Generate a strong secret with: python -c 'import secrets; print(secrets.token_urlsafe(32))'"
            )
        
        # Warn if using default/test values
        weak_secrets = [
            "your-secret-key-change-in-production",
            "test-secret-key-change-in-production",
            "secret",
            "changeme",
            "test"
        ]
        if v.lower() in weak_secrets:
            raise ValueError(
                f"JWT_SECRET_KEY is using a weak/default value. "
                f"Generate a strong secret with: python -c 'import secrets; print(secrets.token_urlsafe(32))'"
            )
        
        return v


# Global settings instance
settings = Settings()
