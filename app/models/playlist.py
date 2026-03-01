"""
Playlist Model
"""
from datetime import datetime
from sqlalchemy import Column, Integer, String, DateTime, ForeignKey, Enum as SQLEnum, Text
from sqlalchemy.orm import relationship

from app.db.base import Base


class PlaylistStatus(str):
    """Playlist status enumeration"""
    SCHEDULED = "scheduled"
    LIVE = "live"
    COMPLETED = "completed"
    CANCELLED = "cancelled"


class Playlist(Base):
    """
    Playlist Model
    
    Represents a scheduled streaming playlist
    """
    __tablename__ = "playlists"
    
    id = Column(Integer, primary_key=True, index=True)
    name = Column(String(255), nullable=False)
    channel_id = Column(Integer, ForeignKey("channels.id"), nullable=False)
    start_time = Column(DateTime, nullable=False)
    status = Column(String(20), default=PlaylistStatus.SCHEDULED, nullable=False)
    video_count = Column(Integer, default=0)
    created_at = Column(DateTime, default=datetime.utcnow)
    updated_at = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)
    description = Column(Text, nullable=True)
    
    # Relationships
    channel = relationship("Channel", back_populates="playlists")
    videos = relationship("PlaylistVideo", back_populates="playlist", cascade="all, delete-orphan")
    
    def __repr__(self):
        return f"<Playlist(id={self.id}, name='{self.name}', status={self.status})>"


class PlaylistVideo(Base):
    """
    Playlist Video Junction Table
    
    Links videos to playlists with order
    """
    __tablename__ = "playlist_videos"
    
    id = Column(Integer, primary_key=True, index=True)
    playlist_id = Column(Integer, ForeignKey("playlists.id"), nullable=False)
    video_id = Column(Integer, ForeignKey("videos.id"), nullable=False)
    order = Column(Integer, default=0, nullable=False)
    created_at = Column(DateTime, default=datetime.utcnow)
    
    # Relationships
    playlist = relationship("Playlist", back_populates="videos")
    video = relationship("Video", back_populates="playlists")
    
    def __repr__(self):
        return f"<PlaylistVideo(playlist_id={self.playlist_id}, video_id={self.video_id}, order={self.order})>"
