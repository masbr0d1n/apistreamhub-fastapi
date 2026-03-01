"""
Playlist Routes
API endpoints for playlist management
"""
from fastapi import APIRouter, Depends, HTTPException, Query
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select
from typing import List

from app.db.base import get_db
from app.schemas.playlist import (
    PlaylistCreate,
    PlaylistUpdate,
    PlaylistResponse,
    PlaylistListResponse,
    PlaylistVideoAdd,
    PlaylistVideoResponse
)
from app.core.security import get_current_user
from app.models.user import User
from app.models.channel import Channel
from app.models.video import Video
from app.services.playlist_service import PlaylistService


router = APIRouter(prefix="/playlists", tags=["playlists"])
playlist_service = PlaylistService()


@router.get("")
async def get_all_playlists(
    skip: int = Query(0, ge=0),
    limit: int = Query(100, ge=1, le=100),
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    """
    Get all playlists for current user
    """
    from app.schemas.playlist import PlaylistListResponse

    playlists = await playlist_service.get_all(db, skip, limit)

    result = []
    for playlist in playlists:
        # Get channel info
        channel_result = await db.execute(
            select(Channel).where(Channel.id == playlist.channel_id)
        )
        channel = channel_result.scalar_one_or_none()

        result.append({
            "id": playlist.id,
            "name": playlist.name,
            "channel_id": playlist.channel_id,
            "channel_name": channel.name if channel else "Unknown",
            "start_time": playlist.start_time,
            "status": playlist.status,
            "video_count": playlist.video_count,
            "created_at": playlist.created_at,
            "updated_at": playlist.updated_at
        })

    return PlaylistListResponse(
        status=True,
        statusCode=200,
        message="Success",
        data=result
    )


@router.get("/{playlist_id}")
async def get_playlist(
    playlist_id: int,
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    """
    Get a specific playlist by ID with videos
    """
    playlist = await playlist_service.get_by_id(db, playlist_id)
    
    # Get channel info
    channel_result = await db.execute(
        select(Channel).where(Channel.id == playlist.channel_id)
    )
    channel = channel_result.scalar_one_or_none()
    
    # Get playlist videos with full video details
    playlist_videos = await playlist_service.get_videos(db, playlist_id)
    
    videos = []
    for pv in playlist_videos:
        # Get video info
        video_result = await db.execute(
            select(Video).where(Video.id == pv.video_id)
        )
        video = video_result.scalar_one_or_none()
        
        if video:
            videos.append({
                "id": video.id,
                "title": video.title,
                "description": video.description,
                "thumbnail_url": video.thumbnail_url,
                "duration": float(video.duration) if video.duration else None,
                "youtube_id": video.youtube_id,
                "channel_id": video.channel_id,
                "view_count": video.view_count,
                "width": video.width,
                "height": video.height,
                "video_codec": video.video_codec,
                "video_bitrate": video.video_bitrate,
                "audio_codec": video.audio_codec,
                "audio_bitrate": video.audio_bitrate,
                "fps": float(video.fps) if video.fps else None,
                "created_at": video.created_at.isoformat() if video.created_at else None,
                "order": pv.order
            })
    
    return {
        "status": True,
        "statusCode": 200,
        "message": "Success",
        "data": {
            "id": playlist.id,
            "name": playlist.name,
            "channel_id": playlist.channel_id,
            "start_time": playlist.start_time,
            "status": playlist.status,
            "video_count": playlist.video_count,
            "description": playlist.description,
            "created_at": playlist.created_at,
            "updated_at": playlist.updated_at,
            "channel_name": channel.name if channel else None,
            "videos": videos
        }
    }


@router.post("", response_model=PlaylistResponse, status_code=201)
async def create_playlist(
    playlist_data: PlaylistCreate,
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    """
    Create a new playlist
    """
    playlist = await playlist_service.create(db, playlist_data, current_user.id)
    
    # Get channel info
    channel_result = await db.execute(
        select(Channel).where(Channel.id == playlist.channel_id)
    )
    channel = channel_result.scalar_one_or_none()
    
    return {
        "id": playlist.id,
        "name": playlist.name,
        "channel_id": playlist.channel_id,
        "start_time": playlist.start_time,
        "status": playlist.status,
        "video_count": playlist.video_count,
        "description": playlist.description,
        "created_at": playlist.created_at,
        "updated_at": playlist.updated_at,
        "channel_name": channel.name if channel else None
    }


@router.put("/{playlist_id}", response_model=PlaylistResponse)
async def update_playlist(
    playlist_id: int,
    playlist_data: PlaylistUpdate,
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    """
    Update a playlist
    """
    playlist = await playlist_service.update(db, playlist_id, playlist_data, current_user.id)
    
    # Get channel info
    channel_result = await db.execute(
        select(Channel).where(Channel.id == playlist.channel_id)
    )
    channel = channel_result.scalar_one_or_none()
    
    return {
        "id": playlist.id,
        "name": playlist.name,
        "channel_id": playlist.channel_id,
        "start_time": playlist.start_time,
        "status": playlist.status,
        "video_count": playlist.video_count,
        "description": playlist.description,
        "created_at": playlist.created_at,
        "updated_at": playlist.updated_at,
        "channel_name": channel.name if channel else None
    }


@router.delete("/{playlist_id}")
async def delete_playlist(
    playlist_id: int,
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    """
    Delete a playlist
    """
    await playlist_service.delete(db, playlist_id, current_user.id)
    
    return {"status": True, "message": "Playlist deleted successfully"}


@router.get("/{playlist_id}/videos", response_model=List[PlaylistVideoResponse])
async def get_playlist_videos(
    playlist_id: int,
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    """
    Get all videos in a playlist
    """
    await playlist_service.get_by_id(db, playlist_id)  # Check if playlist exists
    
    playlist_videos = await playlist_service.get_videos(db, playlist_id)
    
    result = []
    for pv in playlist_videos:
        # Get video info
        video_result = await db.execute(
            select(Video).where(Video.id == pv.video_id)
        )
        video = video_result.scalar_one_or_none()
        
        result.append({
            "id": pv.id,
            "video_id": pv.video_id,
            "video_title": video.title if video else None,
            "video_url": video.url if video else None,
            "order": pv.order
        })
    
    return result


@router.post("/{playlist_id}/videos", response_model=PlaylistVideoResponse, status_code=201)
async def add_video_to_playlist(
    playlist_id: int,
    video_data: PlaylistVideoAdd,
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    """
    Add a video to a playlist
    """
    await playlist_service.get_by_id(db, playlist_id)  # Check if playlist exists
    
    playlist_video = await playlist_service.add_video(
        db, playlist_id, video_data.video_id, video_data.order
    )
    
    # Get video info
    video_result = await db.execute(
        select(Video).where(Video.id == playlist_video.video_id)
    )
    video = video_result.scalar_one_or_none()
    
    return {
        "id": playlist_video.id,
        "video_id": playlist_video.video_id,
        "video_title": video.title if video else None,
        "video_url": video.url if video else None,
        "order": playlist_video.order
    }


@router.delete("/{playlist_id}/videos/{video_id}")
async def remove_video_from_playlist(
    playlist_id: int,
    video_id: int,
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    """
    Remove a video from a playlist
    """
    await playlist_service.remove_video(db, playlist_id, video_id)
    
    return {"status": True, "message": "Video removed from playlist"}


@router.put("/{playlist_id}/videos/")
async def update_playlist_videos(
    playlist_id: int,
    video_ids: dict,
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    """
    Update playlist videos - replaces all videos with new ordered list
    """
    await playlist_service.get_by_id(db, playlist_id)  # Check if playlist exists
    
    # Get list of video IDs
    ids = video_ids.get("video_ids", [])
    
    # Clear existing playlist videos
    await playlist_service.clear_videos(db, playlist_id)
    
    # Add videos in order
    for index, video_id in enumerate(ids):
        await playlist_service.add_video(db, playlist_id, video_id, index)
    
    return {
        "status": True,
        "statusCode": 200,
        "message": "Playlist videos updated successfully",
        "data": {
            "playlist_id": playlist_id,
            "video_count": len(ids)
        }
    }
