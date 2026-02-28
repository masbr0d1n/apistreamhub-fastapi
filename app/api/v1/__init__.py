from fastapi import APIRouter

from app.api.v1 import auth, channels, videos, streaming, playlists

api_router = APIRouter()

api_router.include_router(auth.router, prefix="/auth", tags=["auth"])
api_router.include_router(channels.router, prefix="/channels", tags=["channels"])
api_router.include_router(videos.router, prefix="/videos", tags=["videos"])
api_router.include_router(streaming.router, prefix="/streaming", tags=["streaming"])
api_router.include_router(playlists.router, tags=["playlists"])
