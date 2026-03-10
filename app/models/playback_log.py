"""
Playback Log Model
Tracks content playback for analytics
"""

from sqlalchemy import Column, String, DateTime, ForeignKey, Integer
from sqlalchemy.dialects.postgresql import UUID
from sqlalchemy.sql import func
import uuid

from app.db.base import Base


class PlaybackLog(Base):
    """Tracks when content is played on screens."""
    __tablename__ = "playback_logs"
    
    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    content_id = Column(UUID(as_uuid=True), ForeignKey("videos.id"), nullable=False)
    screen_id = Column(UUID(as_uuid=True), ForeignKey("screens.id"), nullable=False)
    tenant_id = Column(UUID(as_uuid=True), ForeignKey("tenants.id"), nullable=False)
    
    started_at = Column(DateTime(timezone=True), nullable=False)
    ended_at = Column(DateTime(timezone=True), nullable=True)
    duration_played = Column(Integer, default=0)  # in seconds
    
    created_at = Column(DateTime(timezone=True), server_default=func.now())
    
    def __repr__(self):
        return f"<PlaybackLog {self.content_id} on {self.screen_id}>"
