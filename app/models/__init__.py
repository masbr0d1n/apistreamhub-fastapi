"""
Database models
"""
from sqlalchemy.orm import DeclarativeBase

from app.models.user import User, UserRole
from app.models.video import Video
from app.models.channel import Channel
from app.models.screen import Screen, ScreenStatus
from app.models.screen_group import ScreenGroup, ScreenGroupItem
from app.models.layout import Layout
from app.models.campaign import Campaign, CampaignStatus
from app.models.template import Template
from app.models.tenant import Tenant
