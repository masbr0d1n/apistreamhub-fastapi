"""
Role Preset model - Template roles with page access configurations
"""
from datetime import datetime
from sqlalchemy import String, Boolean, JSON, DateTime
from sqlalchemy.orm import Mapped, mapped_column

from app.db.base import Base


class RolePreset(Base):
    """Role preset template for easy user role assignment."""
    
    __tablename__ = "role_presets"
    
    id: Mapped[int] = mapped_column(primary_key=True, autoincrement=True)
    name: Mapped[str] = mapped_column(String(100), nullable=False, unique=True, index=True)
    description: Mapped[str | None] = mapped_column(String(500))
    page_access: Mapped[dict] = mapped_column(JSON, nullable=False, default=lambda: {})
    is_system: Mapped[bool] = mapped_column(Boolean, default=False)  # System presets cannot be deleted
    is_active: Mapped[bool] = mapped_column(Boolean, default=True)
    created_at: Mapped[datetime] = mapped_column(DateTime, default=datetime.utcnow)
    created_by: Mapped[int | None] = mapped_column()  # User ID who created this preset
    
    def __repr__(self) -> str:
        return f"<RolePreset(id={self.id}, name='{self.name}', is_system={self.is_system})>"
