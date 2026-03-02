"""
Database models
"""
from sqlalchemy.orm import DeclarativeBase

from app.models.user import User, UserRole
from app.models.video import Video
from app.models.channel import Channel
