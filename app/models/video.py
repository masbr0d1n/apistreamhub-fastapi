"""
Video model - database schema.
"""
from datetime import datetime
from typing import Optional
from sqlalchemy import String, Integer, DateTime, Text, ForeignKey, Boolean
from sqlalchemy.orm import Mapped, mapped_column
from sqlalchemy.sql import func

from app.db.base import Base


class Video(Base):
    """Video model."""
    
    __tablename__ = "videos"
    
    id: Mapped[int] = mapped_column(primary_key=True, autoincrement=True)
    title: Mapped[str] = mapped_column(String(500), nullable=False, index=True)
    description: Mapped[Optional[str]] = mapped_column(Text, nullable=True)
    youtube_id: Mapped[str] = mapped_column(String(20), nullable=False, unique=True, index=True)
    channel_id: Mapped[int] = mapped_column(Integer, ForeignKey("channels.id"), nullable=False)
    thumbnail_url: Mapped[Optional[str]] = mapped_column(String(500), nullable=True)
    duration: Mapped[Optional[int]] = mapped_column(Integer, nullable=True)  # in seconds
    view_count: Mapped[int] = mapped_column(Integer, default=0)
    is_live: Mapped[bool] = mapped_column(Boolean, default=False)
    is_active: Mapped[bool] = mapped_column(Boolean, default=True)
    created_at: Mapped[datetime] = mapped_column(DateTime, server_default=func.now())
    updated_at: Mapped[datetime] = mapped_column(DateTime, server_default=func.now(), onupdate=func.now())
    
    def __repr__(self) -> str:
        return f"<Video(id={self.id}, title='{self.title}', youtube_id='{self.youtube_id}')>"
