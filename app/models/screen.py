"""
Screen model - database schema for Videotron device management.
"""
import uuid
from datetime import datetime
from typing import Optional
from sqlalchemy import String, DateTime, Enum as SQLEnum, ForeignKey
from sqlalchemy.dialects.postgresql import UUID as PG_UUID
from sqlalchemy.orm import Mapped, mapped_column, relationship
from sqlalchemy.sql import func
import enum

from app.db.base import Base


class ScreenStatus(str, enum.Enum):
    """Screen status enumeration."""
    ONLINE = "online"
    OFFLINE = "offline"
    MAINTENANCE = "maintenance"


class Screen(Base):
    """Screen model for Videotron device management."""
    
    __tablename__ = "screens"
    
    id: Mapped[uuid.UUID] = mapped_column(
        PG_UUID(as_uuid=True), 
        primary_key=True, 
        default=uuid.uuid4
    )
    device_id: Mapped[str] = mapped_column(String(255), unique=True, nullable=False, index=True)
    name: Mapped[str] = mapped_column(String(500), nullable=False, index=True)
    location: Mapped[Optional[str]] = mapped_column(String(500), nullable=True)
    resolution: Mapped[Optional[str]] = mapped_column(String(50), nullable=True)
    status: Mapped[ScreenStatus] = mapped_column(
        SQLEnum(ScreenStatus), 
        default=ScreenStatus.OFFLINE, 
        index=True
    )
    last_heartbeat: Mapped[Optional[datetime]] = mapped_column(DateTime(timezone=True), nullable=True)
    api_key: Mapped[Optional[str]] = mapped_column(String(255), unique=True, nullable=True)
    
    created_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True), 
        server_default=func.now()
    )
    updated_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True), 
        server_default=func.now(), 
        onupdate=func.now()
    )
    
    # Tenant
    tenant_id: Mapped[Optional[uuid.UUID]] = mapped_column(
        PG_UUID(as_uuid=True),
        ForeignKey("tenants.id"),
        nullable=True
    )
    
    # Relationships
    groups = relationship(
        "ScreenGroup",
        secondary="screen_group_items",
        back_populates="screens"
    )
    
    def __repr__(self) -> str:
        return f"<Screen(id={self.id}, device_id='{self.device_id}', name='{self.name}', status={self.status})>"
