"""
Full Playlists API with database integration
"""

from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select, delete
from typing import List, Optional
from datetime import datetime
import uuid

from app.db.base import get_db
from app.schemas.playlist import (
    PlaylistCreate,
    PlaylistUpdate,
    PlaylistResponse,
    PlaylistDetailResponse,
    PlaylistItemCreate,
    PlaylistItemResponse,
    PlaylistListResponse,
)
from app.models.video import Video
from sqlalchemy import text

router = APIRouter(prefix="/api/v1/playlists", tags=["playlists"])


@router.get("/", response_model=List[PlaylistResponse])
async def get_playlists(
    skip: int = 0,
    limit: int = 100,
    published_only: bool = False,
    db: AsyncSession = Depends(get_db),
):
    """Get all playlists"""
    # Query from database
    query = text("""
        SELECT id, name, description, default_duration, transition, loop,
               is_published, items_count, total_duration, used_in,
               created_at, updated_at
        FROM playlists
        WHERE (:published_only = false OR is_published = true)
        ORDER BY created_at DESC
        LIMIT :limit OFFSET :skip
    """)
    
    result = await db.execute(query, {
        "published_only": published_only,
        "limit": limit,
        "skip": skip
    })
    
    playlists = []
    for row in result:
        playlists.append(PlaylistResponse(
            id=row[0],
            name=row[1],
            description=row[2],
            default_duration=row[3],
            transition=row[4],
            loop=row[5],
            is_published=row[6],
            items_count=row[7],
            total_duration=row[8],
            used_in=row[9],
            created_at=row[10],
            updated_at=row[11],
        ))
    
    await db.commit()
    return playlists


@router.get("/{playlist_id}", response_model=PlaylistDetailResponse)
async def get_playlist(
    playlist_id: str,
    db: AsyncSession = Depends(get_db),
):
    """Get playlist by ID with all items"""
    # Get playlist
    playlist_query = text("""
        SELECT id, name, description, default_duration, transition, loop,
               is_published, items_count, total_duration, used_in,
               created_at, updated_at
        FROM playlists
        WHERE id = :playlist_id
    """)
    
    result = await db.execute(playlist_query, {"playlist_id": playlist_id})
    row = result.fetchone()
    
    if not row:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Playlist not found"
        )
    
    # Get items
    items_query = text("""
        SELECT pi.id, pi.playlist_id, pi.media_id, v.title as name,
               pi.duration, pi."order", v.content_type as media_type
        FROM playlist_items pi
        LEFT JOIN videos v ON pi.media_id = CAST(v.id AS VARCHAR)
        WHERE pi.playlist_id = :playlist_id
        ORDER BY pi."order"
    """)
    
    items_result = await db.execute(items_query, {"playlist_id": playlist_id})
    items = []
    for item_row in items_result:
        items.append(PlaylistItemResponse(
            id=item_row[0],
            playlist_id=item_row[1],
            media_id=item_row[2],
            name=item_row[3] or "Unknown",
            duration=item_row[4],
            order=item_row[5],
            media_type=item_row[6] or "video",
        ))
    
    await db.commit()
    
    return PlaylistDetailResponse(
        id=row[0],
        name=row[1],
        description=row[2],
        default_duration=row[3],
        transition=row[4],
        loop=row[5],
        is_published=row[6],
        items_count=row[7],
        total_duration=row[8],
        used_in=row[9],
        created_at=row[10],
        updated_at=row[11],
        items=items,
    )


@router.post("/", response_model=PlaylistResponse, status_code=status.HTTP_201_CREATED)
async def create_playlist(
    playlist: PlaylistCreate,
    db: AsyncSession = Depends(get_db),
):
    """Create a new playlist or draft"""
    import uuid

    # Check if playlist name already exists
    name_check_query = text("SELECT id FROM playlists WHERE name = :name")
    existing = await db.execute(name_check_query, {"name": playlist.name})
    if existing.fetchone():
        raise HTTPException(
            status_code=status.HTTP_409_CONFLICT,
            detail=f"Playlist with name '{playlist.name}' already exists"
        )

    playlist_id = str(uuid.uuid4())
    
    query = text("""
        INSERT INTO playlists (id, name, description, default_duration, transition, loop, is_published)
        VALUES (:id, :name, :description, :default_duration, :transition, :loop, :is_published)
        RETURNING id, name, description, default_duration, transition, loop, is_published,
                  items_count, total_duration, used_in, created_at, updated_at
    """)
    
    result = await db.execute(query, {
        "id": playlist_id,
        "name": playlist.name,
        "description": playlist.description,
        "default_duration": playlist.default_duration,
        "transition": playlist.transition,
        "loop": playlist.loop,
        "is_published": playlist.is_published,
    })
    
    row = result.fetchone()
    
    # Insert items if provided
    items_count = 0
    total_duration = 0
    if playlist.items:
        items_count, total_duration = await insert_playlist_items(playlist_id, playlist.items, db)
        
        # Update playlist stats
        update_stats = text("""
            UPDATE playlists
            SET items_count = :items_count,
                total_duration = :total_duration,
                updated_at = CURRENT_TIMESTAMP
            WHERE id = :playlist_id
        """)
        await db.execute(update_stats, {
            "playlist_id": playlist_id,
            "items_count": items_count,
            "total_duration": total_duration,
        })
    
    await db.commit()
    
    return PlaylistResponse(
        id=row[0],
        name=row[1],
        description=row[2],
        default_duration=row[3],
        transition=row[4],
        loop=row[5],
        is_published=row[6],
        items_count=items_count,
        total_duration=total_duration,
        used_in=0,
        created_at=row[10],
        updated_at=row[11],
    )


async def insert_playlist_items(
    playlist_id: str,
    items: List,
    db: AsyncSession
):
    """Helper function to insert playlist items"""
    if not items:
        return 0, 0

    total_duration = 0
    for idx, item in enumerate(items, start=1):
        item_id = str(uuid.uuid4())
        # Use attribute access for Pydantic models, not dict.get()
        item_order = item.order if item.order else idx
        item_media_id = str(item.media_id) if item.media_id else ''
        item_duration = int(item.duration) if item.duration else 10

        # Insert only columns that exist in the table
        # name and media_type can be fetched via JOIN from videos table
        insert_query = text("""
            INSERT INTO playlist_items (id, playlist_id, media_id, duration, "order")
            VALUES (:id, :playlist_id, :media_id, :duration, :order)
        """)

        await db.execute(insert_query, {
            "id": item_id,
            "playlist_id": playlist_id,
            "media_id": item_media_id,
            "duration": item_duration,
            "order": item_order,
        })

        total_duration += item_duration

    return len(items), total_duration


@router.post("/draft", response_model=PlaylistResponse, status_code=status.HTTP_201_CREATED)
async def save_draft(
    playlist: PlaylistCreate,
    db: AsyncSession = Depends(get_db),
):
    """Save playlist as draft"""
    import uuid
    playlist_id = str(uuid.uuid4())
    
    query = text("""
        INSERT INTO playlists (id, name, description, default_duration, transition, loop, is_published)
        VALUES (:id, :name, :description, :default_duration, :transition, :loop, false)
        RETURNING id, name, description, default_duration, transition, loop, is_published,
                  items_count, total_duration, used_in, created_at, updated_at
    """)
    
    result = await db.execute(query, {
        "id": playlist_id,
        "name": playlist.name,
        "description": playlist.description,
        "default_duration": playlist.default_duration,
        "transition": playlist.transition,
        "loop": playlist.loop,
    })
    
    row = result.fetchone()
    
    # Insert items if provided
    items_count = 0
    total_duration = 0
    if playlist.items:
        items_count, total_duration = await insert_playlist_items(playlist_id, playlist.items, db)
        
        # Update playlist stats
        update_stats = text("""
            UPDATE playlists
            SET items_count = :items_count,
                total_duration = :total_duration,
                updated_at = CURRENT_TIMESTAMP
            WHERE id = :playlist_id
        """)
        await db.execute(update_stats, {
            "playlist_id": playlist_id,
            "items_count": items_count,
            "total_duration": total_duration,
        })
    
    await db.commit()
    
    return PlaylistResponse(
        id=row[0],
        name=row[1],
        description=row[2],
        default_duration=row[3],
        transition=row[4],
        loop=row[5],
        is_published=False,
        items_count=items_count,
        total_duration=total_duration,
        used_in=0,
        created_at=row[10],
        updated_at=row[11],
    )


@router.put("/{playlist_id}", response_model=PlaylistResponse)
async def update_playlist(
    playlist_id: str,
    playlist: PlaylistCreate,
    db: AsyncSession = Depends(get_db),
):
    """Update existing playlist and replace all items"""
    # Check if name already exists in OTHER playlists
    name_check_query = text("SELECT id FROM playlists WHERE name = :name AND id != :playlist_id")
    existing = await db.execute(name_check_query, {"name": playlist.name, "playlist_id": playlist_id})
    if existing.fetchone():
        raise HTTPException(
            status_code=status.HTTP_409_CONFLICT,
            detail=f"Playlist with name '{playlist.name}' already exists"
        )

    # Update playlist properties
    update_query = text("""
        UPDATE playlists
        SET name = :name,
            description = :description,
            default_duration = :default_duration,
            transition = :transition,
            loop = :loop,
            updated_at = CURRENT_TIMESTAMP
        WHERE id = :playlist_id
        RETURNING id, name, description, default_duration, transition, loop,
                  is_published, items_count, total_duration, used_in,
                  created_at, updated_at
    """)
    
    result = await db.execute(update_query, {
        "playlist_id": playlist_id,
        "name": playlist.name,
        "description": playlist.description,
        "default_duration": playlist.default_duration,
        "transition": playlist.transition,
        "loop": playlist.loop,
    })
    
    row = result.fetchone()
    
    if not row:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Playlist not found"
        )
    
    # Delete existing items
    delete_items_query = text("""
        DELETE FROM playlist_items
        WHERE playlist_id = :playlist_id
    """)
    await db.execute(delete_items_query, {"playlist_id": playlist_id})
    
    # Insert new items if provided
    items_count = 0
    total_duration = 0
    if playlist.items:
        items_count, total_duration = await insert_playlist_items(playlist_id, playlist.items, db)
        
        # Update playlist stats
        update_stats = text("""
            UPDATE playlists
            SET items_count = :items_count,
                total_duration = :total_duration,
                updated_at = CURRENT_TIMESTAMP
            WHERE id = :playlist_id
        """)
        await db.execute(update_stats, {
            "playlist_id": playlist_id,
            "items_count": items_count,
            "total_duration": total_duration,
        })
    
    await db.commit()
    
    return PlaylistResponse(
        id=row[0],
        name=row[1],
        description=row[2],
        default_duration=row[3],
        transition=row[4],
        loop=row[5],
        is_published=row[6],
        items_count=items_count,
        total_duration=total_duration,
        used_in=row[9],
        created_at=row[10],
        updated_at=row[11],
    )


@router.post("/{playlist_id}/items", response_model=PlaylistItemResponse, status_code=status.HTTP_201_CREATED)
async def add_playlist_item(
    playlist_id: str,
    item: PlaylistItemCreate,
    db: AsyncSession = Depends(get_db),
):
    """Add media item to playlist timeline"""
    # Verify playlist exists
    playlist_check = text("SELECT id FROM playlists WHERE id = :playlist_id")
    result = await db.execute(playlist_check, {"playlist_id": playlist_id})
    if not result.fetchone():
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Playlist not found"
        )
    
    # Get next order number
    order_query = text("""
        SELECT COALESCE(MAX("order"), 0) + 1
        FROM playlist_items
        WHERE playlist_id = :playlist_id
    """)
    order_result = await db.execute(order_query, {"playlist_id": playlist_id})
    next_order = order_result.scalar() or 1
    
    # Get media info
    media_query = text("SELECT id, title, content_type FROM videos WHERE CAST(id AS VARCHAR) = :media_id")
    media_result = await db.execute(media_query, {"media_id": item.media_id})
    media_row = media_result.fetchone()
    
    if not media_row:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Media not found"
        )
    
    # Create item
    item_id = str(uuid.uuid4())
    insert_query = text("""
        INSERT INTO playlist_items (id, playlist_id, media_id, duration, "order")
        VALUES (:id, :playlist_id, :media_id, :duration, :order)
        RETURNING id, playlist_id, media_id, duration, "order"
    """)
    
    result = await db.execute(insert_query, {
        "id": item_id,
        "playlist_id": playlist_id,
        "media_id": item.media_id,
        "duration": item.duration,
        "order": next_order,
    })
    
    row = result.fetchone()
    
    # Update playlist stats
    update_stats = text("""
        UPDATE playlists
        SET items_count = (SELECT COUNT(*) FROM playlist_items WHERE playlist_id = :playlist_id),
            total_duration = (SELECT COALESCE(SUM(duration), 0) FROM playlist_items WHERE playlist_id = :playlist_id),
            updated_at = CURRENT_TIMESTAMP
        WHERE id = :playlist_id
    """)
    await db.execute(update_stats, {"playlist_id": playlist_id})
    
    await db.commit()
    
    return PlaylistItemResponse(
        id=row[0],
        playlist_id=row[1],
        media_id=row[2],
        name=media_row[1] or "Unknown",
        duration=row[4],
        order=row[5],
        media_type=media_row[2] or "video",
    )


@router.post("/{playlist_id}/items/reorder", status_code=status.HTTP_200_OK)
async def reorder_playlist_items(
    playlist_id: str,
    item_orders: dict[str, int],
    db: AsyncSession = Depends(get_db),
):
    """Reorder playlist items (drag & drop)"""
    # Update each item's order
    for item_id, new_order in item_orders.items():
        update_query = text("""
            UPDATE playlist_items
            SET "order" = :new_order
            WHERE id = :item_id AND playlist_id = :playlist_id
        """)
        await db.execute(update_query, {
            "item_id": item_id,
            "playlist_id": playlist_id,
            "new_order": new_order,
        })
    
    await db.commit()
    
    return {"message": "Items reordered successfully"}


@router.delete("/{playlist_id}", status_code=status.HTTP_204_NO_CONTENT)
async def delete_playlist(
    playlist_id: str,
    db: AsyncSession = Depends(get_db),
):
    """Delete a playlist (cascade deletes items)"""
    delete_query = text("DELETE FROM playlists WHERE id = :playlist_id")
    result = await db.execute(delete_query, {"playlist_id": playlist_id})
    
    if result.rowcount == 0:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Playlist not found"
        )
    
    await db.commit()
    return None
