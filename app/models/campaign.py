"""
Campaign model - database schema for Videotron campaign management.
"""
import uuid
from datetime import datetime
from typing import Optional
from sqlalchemy import String, DateTime, ForeignKey, Integer, Enum as SQLEnum, Text
from sqlalchemy.dialects.postgresql import UUID as PG_UUID, JSONB
from sqlalchemy.orm import Mapped, mapped_column
from sqlalchemy.sql import func
import enum

from app.db.base import Base


class CampaignStatus(str, enum.Enum):
    """Campaign status enumeration."""
    DRAFT = "draft"
    ACTIVE = "active"
    PAUSED = "paused"
    COMPLETED = "completed"


class Campaign(Base):
    """Campaign model for Videotron campaign management."""
    
    __tablename__ = "campaigns"
    
    id: Mapped[uuid.UUID] = mapped_column(
        PG_UUID(as_uuid=True), 
        primary_key=True, 
        default=uuid.uuid4
    )
    name: Mapped[str] = mapped_column(String(500), nullable=False, index=True)
    description: Mapped[Optional[str]] = mapped_column(Text, nullable=True)
    screen_ids: Mapped[list] = mapped_column(
        JSONB, 
        nullable=True, 
        default=list,
        comment="Array of screen UUIDs"
    )
    layout_ids: Mapped[list] = mapped_column(
        JSONB, 
        nullable=True, 
        default=list,
        comment="Array of layout UUIDs"
    )
    status: Mapped[str] = mapped_column(
        String(20),
        server_default="draft",
        default="draft",
        nullable=False,
        index=True,
        comment="Campaign status: draft, active, paused, completed"
    )
    start_date: Mapped[Optional[datetime]] = mapped_column(
        DateTime(timezone=True), 
        nullable=True
    )
    end_date: Mapped[Optional[datetime]] = mapped_column(
        DateTime(timezone=True), 
        nullable=True
    )
    created_by: Mapped[Optional[int]] = mapped_column(
        Integer, 
        ForeignKey("users.id", ondelete="SET NULL"), 
        nullable=True,
        index=True
    )
    
    created_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True), 
        server_default=func.now()
    )
    updated_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True), 
        server_default=func.now(), 
        onupdate=func.now()
    )
    
    def __repr__(self) -> str:
        return f"<Campaign(id={self.id}, name='{self.name}', status={self.status.value})>"
