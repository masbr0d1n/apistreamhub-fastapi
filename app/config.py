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
        default="postgresql+asyncpg://user:password@localhost:5432/apistreamhub"
    )
    
    # JWT
    JWT_SECRET_KEY: str = Field(
        default="your-secret-key-change-in-production"
    )
    JWT_ALGORITHM: str = "HS256"
    ACCESS_TOKEN_EXPIRE_MINUTES: int = 60 * 24 * 3  # 3 days
    REFRESH_TOKEN_EXPIRE_DAYS: int = 30
    
    # CORS
    CORS_ORIGINS: List[str] = [
        "http://localhost:3000",
        "http://localhost:9000",
        "http://localhost:3300",
        "http://192.168.200.60:3000",
        "https://streamhub.uzone.id",
        "https://api-streamhub.uzone.id"
    ]
    
    # File Upload
    UPLOAD_DIR: str = "uploads/"
    MAX_UPLOAD_SIZE: int = 10 * 1024 * 1024  # 10MB
    
    # Telegram
    TELEGRAM_BOT_TOKEN: str = ""
    TELEGRAM_CHAT_ID: str = ""
    
    @field_validator("CORS_ORIGINS", mode="before")
    @classmethod
    def parse_cors_origins(cls, v):
        if isinstance(v, str):
            return [origin.strip() for origin in v.split(",")]
        return v


# Global settings instance
settings = Settings()
