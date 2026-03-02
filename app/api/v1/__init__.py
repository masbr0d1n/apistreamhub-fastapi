"""
API v1 routes
"""
from fastapi import APIRouter

from app.api.v1 import auth, channels, videos, streaming, users, role_presets

api_router = APIRouter()

api_router.include_router(auth.router, prefix="/auth", tags=["auth"])
api_router.include_router(channels.router, prefix="/channels", tags=["channels"])
api_router.include_router(videos.router, prefix="/videos", tags=["videos"])
api_router.include_router(streaming.router, prefix="/streaming", tags=["streaming"])
api_router.include_router(users.router, prefix="/users", tags=["users"])
api_router.include_router(role_presets.router, prefix="/role-presets", tags=["role-presets"])
