#!/usr/bin/env python3
"""
Create database tables for playlists
Run this to add playlist tables to existing database
"""

from app.db.base import engine, Base, SessionLocal
from app.models.playlist import Playlist, PlaylistItem
from sqlalchemy import text


def create_tables():
    """Create playlist tables"""
    print("Creating playlist tables...")

    # Create tables
    Base.metadata.create_all(bind=engine)

    print("✓ Tables created successfully")


def verify_tables():
    """Verify tables exist"""
    db = SessionLocal()

    try:
        # Check if tables exist
        result = db.execute(text("""
            SELECT table_name
            FROM information_schema.tables
            WHERE table_schema = 'public'
            AND table_name IN ('playlists', 'playlist_items')
        """))

        tables = [row[0] for row in result]

        print("\n=== Tables Verification ===")
        for table in ['playlists', 'playlist_items']:
            if table in tables:
                print(f"✓ {table} table exists")
            else:
                print(f"✗ {table} table NOT found")

        db.commit()

    except Exception as e:
        print(f"Error: {e}")
        db.rollback()
    finally:
        db.close()


if __name__ == "__main__":
    create_tables()
    verify_tables()
    print("\n=== DONE ===")
