"""
User model - database schema.
"""
from datetime import datetime
from sqlalchemy import String, Boolean, DateTime, JSON, Enum as SQLEnum
from sqlalchemy.orm import Mapped, mapped_column
import enum

from app.db.base import Base


class UserRole(str, enum.Enum):
    """User roles with hierarchy."""
    SUPERADMIN = "superadmin"  # Full access, can manage admins
    ADMIN = "admin"            # Can manage regular users
    USER = "user"              # Regular user


class User(Base):
    """User model for authentication."""
    
    __tablename__ = "users"
    
    id: Mapped[int] = mapped_column(primary_key=True, autoincrement=True)
    username: Mapped[str] = mapped_column(String(100), nullable=False, unique=True, index=True)
    email: Mapped[str] = mapped_column(String(255), nullable=False, unique=True, index=True)
    hashed_password: Mapped[str] = mapped_column(String(255), nullable=False)
    full_name: Mapped[str] = mapped_column(String(255), nullable=False)
    is_active: Mapped[bool] = mapped_column(Boolean, default=True)
    is_admin: Mapped[bool] = mapped_column(Boolean, default=False)  # Deprecated, kept for compatibility
    role: Mapped[str] = mapped_column(SQLEnum(UserRole), default=UserRole.USER, nullable=False)
    page_access: Mapped[dict | None] = mapped_column(JSON, nullable=True)  # Page permissions
    created_at: Mapped[datetime] = mapped_column(DateTime, default=datetime.utcnow)
    last_login: Mapped[datetime] = mapped_column(DateTime, nullable=True)
    
    def __repr__(self) -> str:
        return f"<User(id={self.id}, username='{self.username}', role='{self.role}')>"
    
    def has_page_access(self, page: str) -> bool:
        """Check if user has access to a specific page."""
        if self.role == UserRole.SUPERADMIN:
            return True
        if not self.page_access:
            return True  # No restrictions by default
        return self.page_access.get(page, True)
    
    def can_manage_user(self, target_role: str) -> bool:
        """Check if user can manage another user."""
        if self.role == UserRole.SUPERADMIN:
            return True
        if self.role == UserRole.ADMIN:
            return target_role == UserRole.USER
        return False
