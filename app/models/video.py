"""
Video model - database schema.
"""
from datetime import datetime, date
from typing import Optional, List
from sqlalchemy import String, Integer, DateTime, Text, ForeignKey, Boolean, Numeric, Date, ARRAY
from sqlalchemy.orm import Mapped, mapped_column, relationship
from sqlalchemy.sql import func

from app.db.base import Base


class Video(Base):
    """Video model."""
    
    __tablename__ = "videos"
    
    id: Mapped[int] = mapped_column(primary_key=True, autoincrement=True)
    title: Mapped[str] = mapped_column(String(500), nullable=False, index=True)
    description: Mapped[Optional[str]] = mapped_column(Text, nullable=True)
    youtube_id: Mapped[Optional[str]] = mapped_column(String(255), nullable=True, index=True)  # Made optional for uploaded videos
    channel_id: Mapped[int] = mapped_column(Integer, ForeignKey("channels.id"), nullable=False)
    video_url: Mapped[Optional[str]] = mapped_column(String(500), nullable=True)  # For uploaded videos
    thumbnail_url: Mapped[Optional[str]] = mapped_column(String(500), nullable=True)
    thumbnail_data: Mapped[Optional[str]] = mapped_column(Text, nullable=True)  # Base64 thumbnail for uploaded videos
    duration: Mapped[Optional[float]] = mapped_column(Numeric, nullable=True)  # in seconds (float for FFmpeg)
    view_count: Mapped[int] = mapped_column(Integer, default=0)
    is_live: Mapped[bool] = mapped_column(Boolean, default=False)
    is_active: Mapped[bool] = mapped_column(Boolean, default=True)
    
    # Video metadata (from FFmpeg)
    width: Mapped[Optional[int]] = mapped_column(Integer, nullable=True)  # Video width
    height: Mapped[Optional[int]] = mapped_column(Integer, nullable=True)  # Video height
    video_codec: Mapped[Optional[str]] = mapped_column(String(50), nullable=True)  # Video codec (h264, h265, etc.)
    video_bitrate: Mapped[Optional[int]] = mapped_column(Integer, nullable=True)  # Video bitrate in bps
    audio_codec: Mapped[Optional[str]] = mapped_column(String(50), nullable=True)  # Audio codec (aac, mp3, etc.)
    audio_bitrate: Mapped[Optional[int]] = mapped_column(Integer, nullable=True)  # Audio bitrate in bps
    fps: Mapped[Optional[float]] = mapped_column(Numeric, nullable=True)  # Frames per second
    
    # Additional fields
    tags: Mapped[Optional[List[str]]] = mapped_column(ARRAY(String), nullable=True)  # PostgreSQL array for tags
    expiry_date: Mapped[Optional[date]] = mapped_column(Date, nullable=True)  # Expiry date
    content_type: Mapped[Optional[str]] = mapped_column(String(10), nullable=True)  # 'video' or 'image'
    
    created_at: Mapped[datetime] = mapped_column(DateTime, server_default=func.now())
    updated_at: Mapped[datetime] = mapped_column(DateTime, server_default=func.now(), onupdate=func.now())
    
    # Relationships
    channel = relationship("Channel", back_populates="videos")
    playlists = relationship("PlaylistVideo", back_populates="video")
    
    @property
    def resolution(self) -> Optional[str]:
        """Get resolution as string (e.g., '1920x1080')"""
        if self.width and self.height:
            return f"{self.width}x{self.height}"
        return None
    
    @property
    def video_bitrate_mbps(self) -> Optional[float]:
        """Get video bitrate in Mbps"""
        if self.video_bitrate:
            return round(self.video_bitrate / 1_000_000, 2)
        return None
    
    @property
    def audio_bitrate_kbps(self) -> Optional[float]:
        """Get audio bitrate in kbps"""
        if self.audio_bitrate:
            return round(self.audio_bitrate / 1_000, 2)
        return None
    
    def __repr__(self) -> str:
        return f"<Video(id={self.id}, title='{self.title}', youtube_id='{self.youtube_id}')>"
