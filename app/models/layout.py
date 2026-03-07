"""
Layout model - database schema for Videotron layout management.
"""
import uuid
from datetime import datetime
from typing import Optional
from sqlalchemy import String, DateTime, ForeignKey, Integer
from sqlalchemy.dialects.postgresql import UUID as PG_UUID, JSONB
from sqlalchemy.orm import Mapped, mapped_column
from sqlalchemy.sql import func

from app.db.base import Base


class Layout(Base):
    """Layout model for Videotron composer."""
    
    __tablename__ = "layouts"
    
    id: Mapped[uuid.UUID] = mapped_column(
        PG_UUID(as_uuid=True), 
        primary_key=True, 
        default=uuid.uuid4
    )
    name: Mapped[str] = mapped_column(String(500), nullable=False, index=True)
    canvas_config: Mapped[dict] = mapped_column(JSONB, nullable=True, comment="Canvas configuration (width, height, orientation)")
    layers: Mapped[dict] = mapped_column(JSONB, nullable=True, comment="Array of layer objects")
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
        return f"<Layout(id={self.id}, name='{self.name}', created_by={self.created_by})>"
