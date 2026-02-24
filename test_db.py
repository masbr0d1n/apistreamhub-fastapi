#!/usr/bin/env python
"""
Test database connection.
"""
import asyncio
import os
from dotenv import load_dotenv

load_dotenv('.env.dev')

async def test_connection():
    """Test PostgreSQL connection."""
    import asyncpg
    
    db_url = os.getenv('DATABASE_URL')
    print(f"Testing connection to: {db_url}")
    
    try:
        conn = await asyncpg.connect(
            host='localhost',
            port=5433,
            user='postgres',
            password='postgres',
            database='apistreamhub'
        )
        result = await conn.fetchval('SELECT version()')
        print(f"✅ Connected successfully!")
        print(f"PostgreSQL version: {result[:50]}...")
        await conn.close()
        return True
    except Exception as e:
        print(f"❌ Connection failed: {e}")
        return False


if __name__ == "__main__":
    result = asyncio.run(test_connection())
    exit(0 if result else 1)
