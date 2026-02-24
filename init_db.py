#!/usr/bin/env python
"""
Initialize database tables.
"""
import asyncio
from app.db.base import engine, Base
from app.models.user import User
from app.models.channel import Channel
from app.models.video import Video


async def create_tables():
    """Create all database tables."""
    async with engine.begin() as conn:
        # Create tables
        await conn.run_sync(Base.metadata.create_all)
        print("✅ Database tables created!")


if __name__ == "__main__":
    asyncio.run(create_tables())
