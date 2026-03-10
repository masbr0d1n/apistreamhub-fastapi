"""
Analytics API endpoints for Videotron.
Provides playback trends, top content, and screen status aggregation.
"""

from fastapi import APIRouter, Depends, Query
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select, func, and_, desc, cast, Date
from datetime import datetime, timedelta
from typing import Optional, List

from app.db.base import get_db
from app.models.video import Video
from app.models.screen import Screen
from app.models.playback_log import PlaybackLog
from app.core.security import get_current_user
from app.models.user import User

router = APIRouter(prefix="/analytics", tags=["analytics"])


@router.get("/playback-trends")
async def get_playback_trends(
    start_date: str = Query(..., description="Start date (YYYY-MM-DD)"),
    end_date: str = Query(..., description="End date (YYYY-MM-DD)"),
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    """
    Get daily playback trends for date range.
    Returns views per day and unique screens count.
    """
    try:
        start = datetime.strptime(start_date, "%Y-%m-%d")
        end = datetime.strptime(end_date, "%Y-%m-%d")
        
        # Query playback logs aggregated by date
        result = await db.execute(
            select(
                cast(PlaybackLog.started_at, Date).label("date"),
                func.count(PlaybackLog.id).label("views"),
                func.count(func.distinct(PlaybackLog.screen_id)).label("unique_screens")
            )
            .where(
                and_(
                    PlaybackLog.tenant_id == current_user.tenant_id,
                    PlaybackLog.started_at >= start,
                    PlaybackLog.started_at <= end + timedelta(days=1)
                )
            )
            .group_by(cast(PlaybackLog.started_at, Date))
            .order_by(cast(PlaybackLog.started_at, Date))
        )
        
        rows = result.all()
        
        # Fill in missing dates with zero values
        date_map = {row.date.strftime("%Y-%m-%d"): {
            "date": row.date.strftime("%Y-%m-%d"),
            "views": row.views,
            "unique_screens": row.unique_screens
        } for row in rows}
        
        # Generate all dates in range
        data = []
        current = start
        while current <= end:
            date_str = current.strftime("%Y-%m-%d")
            if date_str in date_map:
                data.append(date_map[date_str])
            else:
                data.append({
                    "date": date_str,
                    "views": 0,
                    "unique_screens": 0
                })
            current += timedelta(days=1)
        
        return {
            "status": True,
            "data": data
        }
    except Exception as e:
        return {
            "status": False,
            "error": str(e),
            "data": []
        }


@router.get("/top-content")
async def get_top_content(
    limit: int = Query(10, ge=1, le=50),
    start_date: Optional[str] = None,
    end_date: Optional[str] = None,
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    """
    Get top performing content by play count.
    """
    try:
        # Build date filter
        date_filter = True
        if start_date and end_date:
            start = datetime.strptime(start_date, "%Y-%m-%d")
            end = datetime.strptime(end_date, "%Y-%m-%d") + timedelta(days=1)
            date_filter = and_(
                PlaybackLog.started_at >= start,
                PlaybackLog.started_at <= end
            )
        
        # Query top content by play count
        result = await db.execute(
            select(
                PlaybackLog.content_id,
                Video.title,
                func.count(PlaybackLog.id).label("play_count"),
                func.sum(PlaybackLog.duration_played).label("total_duration")
            )
            .join(Video, PlaybackLog.content_id == Video.id)
            .where(
                and_(
                    PlaybackLog.tenant_id == current_user.tenant_id,
                    date_filter
                )
            )
            .group_by(PlaybackLog.content_id, Video.title)
            .order_by(desc("play_count"))
            .limit(limit)
        )
        
        rows = result.all()
        
        data = [{
            "content_id": str(row.content_id),
            "title": row.title,
            "play_count": row.play_count,
            "total_duration": row.total_duration or 0
        } for row in rows]
        
        return {
            "status": True,
            "data": data
        }
    except Exception as e:
        return {
            "status": False,
            "error": str(e),
            "data": []
        }


@router.get("/screen-status")
async def get_screen_status(
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    """
    Get current screen status aggregation.
    """
    try:
        # Query actual screens from database
        result = await db.execute(
            select(Screen.status, func.count(Screen.id).label("count"))
            .where(Screen.tenant_id == current_user.tenant_id)
            .group_by(Screen.status)
        )
        rows = result.all()
        
        # Build response
        status_counts = {"online": 0, "offline": 0, "maintenance": 0}
        total = 0
        for row in rows:
            if row.status in status_counts:
                status_counts[row.status] = row.count
                total += row.count
        
        return {
            "status": True,
            "data": {
                "online": status_counts["online"],
                "offline": status_counts["offline"],
                "maintenance": status_counts["maintenance"],
                "total": total
            }
        }
    except Exception as e:
        return {
            "status": False,
            "error": str(e),
            "data": {
                "online": 0,
                "offline": 0,
                "maintenance": 0,
                "total": 0
            }
        }


@router.post("/playback-log")
async def create_playback_log(
    content_id: str,
    screen_id: str,
    started_at: datetime,
    ended_at: Optional[datetime] = None,
    duration_played: int = 0,
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    """
    Create a playback log entry (called when content starts/ends playing).
    """
    try:
        log = PlaybackLog(
            content_id=content_id,
            screen_id=screen_id,
            tenant_id=current_user.tenant_id,
            started_at=started_at,
            ended_at=ended_at,
            duration_played=duration_played
        )
        db.add(log)
        await db.commit()
        
        return {
            "status": True,
            "data": {"id": str(log.id)}
        }
    except Exception as e:
        return {
            "status": False,
            "error": str(e)
        }
