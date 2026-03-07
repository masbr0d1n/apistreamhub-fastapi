"""
Screen Group model - database schema for grouping screens.
"""
import uuid
from datetime import datetime
from typing import List, Optional
from sqlalchemy import String, DateTime, ForeignKey
from sqlalchemy.dialects.postgresql import UUID as PG_UUID
from sqlalchemy.orm import Mapped, mapped_column, relationship
from sqlalchemy.sql import func

from app.db.base import Base


class ScreenGroupItem(Base):
    """Junction table for many-to-many relationship between ScreenGroup and Screen."""
    
    __tablename__ = "screen_group_items"
    
    id: Mapped[uuid.UUID] = mapped_column(
        PG_UUID(as_uuid=True),
        primary_key=True,
        default=uuid.uuid4
    )
    group_id: Mapped[uuid.UUID] = mapped_column(
        PG_UUID(as_uuid=True),
        ForeignKey("screen_groups.id", ondelete="CASCADE"),
        nullable=False,
        index=True
    )
    screen_id: Mapped[uuid.UUID] = mapped_column(
        PG_UUID(as_uuid=True),
        ForeignKey("screens.id", ondelete="CASCADE"),
        nullable=False,
        index=True
    )
    
    created_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True),
        server_default=func.now()
    )
    
    # Unique constraint on group_id + screen_id
    __table_args__ = (
        # This is handled at DB level with UNIQUE constraint
    )
    
    def __repr__(self) -> str:
        return f"<ScreenGroupItem(group_id={self.group_id}, screen_id={self.screen_id})>"


class ScreenGroup(Base):
    """Screen Group model for organizing screens into groups."""
    
    __tablename__ = "screen_groups"
    
    id: Mapped[uuid.UUID] = mapped_column(
        PG_UUID(as_uuid=True),
        primary_key=True,
        default=uuid.uuid4
    )
    name: Mapped[str] = mapped_column(String(500), nullable=False, index=True)
    
    created_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True),
        server_default=func.now()
    )
    
    # Relationships
    screens = relationship(
        "Screen",
        secondary="screen_group_items",
        back_populates="groups"
    )
    items = relationship(
        "ScreenGroupItem",
        back_populates="group",
        cascade="all, delete-orphan"
    )
    
    def __repr__(self) -> str:
        return f"<ScreenGroup(id={self.id}, name='{self.name}')>"


# Add back_populates to ScreenGroupItem
ScreenGroupItem.group = relationship("ScreenGroup", back_populates="items")
