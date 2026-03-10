"""
Pytest configuration and fixtures for StreamHub API tests.
"""
import pytest
import asyncio
import json
from typing import AsyncGenerator, Generator
from httpx import AsyncClient, ASGITransport
from sqlalchemy.ext.asyncio import AsyncSession, create_async_engine, async_sessionmaker
from sqlalchemy.pool import StaticPool
from sqlalchemy.types import TypeDecorator, Text
from sqlalchemy.ext.compiler import compiles
from sqlalchemy.sql import sqltypes as sql_types
from sqlalchemy.dialects.postgresql import JSONB

from app.main import app
from app.config import settings
from app.db.base import Base, get_db
from app.schemas.auth import UserCreate
from app.services.auth_service import AuthService


# Test database URL (in-memory SQLite for fast tests)
TEST_DATABASE_URL = "sqlite+aiosqlite:///:memory:"


# Register custom compilers for PostgreSQL-specific types to work with SQLite
@compiles(sql_types.ARRAY, 'sqlite')
def compile_array(element, compiler, **kw):
    """Compile ARRAY type as JSON for SQLite compatibility."""
    return "JSON"


@compiles(sql_types.JSON, 'sqlite')
def compile_json(element, compiler, **kw):
    """Compile JSON type for SQLite."""
    return "JSON"


@compiles(JSONB, 'sqlite')
def compile_jsonb(element, compiler, **kw):
    """Compile JSONB type as JSON for SQLite compatibility."""
    return "JSON"


@pytest.fixture(scope="session")
def event_loop() -> Generator:
    """Create an instance of the default event loop for each test session."""
    loop = asyncio.get_event_loop_policy().new_event_loop()
    yield loop
    loop.close()


@pytest.fixture(scope="function")
async def test_engine():
    """Create a test database engine."""
    engine = create_async_engine(
        TEST_DATABASE_URL,
        connect_args={"check_same_thread": False},
        poolclass=StaticPool,
    )
    
    # Create tables
    async with engine.begin() as conn:
        await conn.run_sync(Base.metadata.create_all)
    
    yield engine
    
    # Cleanup
    async with engine.begin() as conn:
        await conn.run_sync(Base.metadata.drop_all)
    
    await engine.dispose()


@pytest.fixture(scope="function")
async def test_db(test_engine) -> AsyncGenerator[AsyncSession, None]:
    """Create a test database session."""
    async_session = async_sessionmaker(
        test_engine, class_=AsyncSession, expire_on_commit=False
    )
    
    async with async_session() as session:
        yield session


@pytest.fixture(scope="function")
async def client(test_db: AsyncSession) -> AsyncGenerator[AsyncClient, None]:
    """Create a test client."""
    # Override the database dependency
    async def override_get_db():
        yield test_db
    
    app.dependency_overrides[get_db] = override_get_db
    
    async with AsyncClient(
        transport=ASGITransport(app=app),
        base_url="http://test"
    ) as ac:
        yield ac
    
    app.dependency_overrides.clear()


@pytest.fixture(scope="function")
async def test_user(test_db: AsyncSession):
    """Create a test user."""
    user_data = UserCreate(
        username="testuser",
        email="test@example.com",
        full_name="Test User",
        password="password123"
    )
    
    auth_service = AuthService()
    user = await auth_service.register(test_db, user_data)
    return user


@pytest.fixture(scope="function")
async def auth_headers(client: AsyncClient, test_user):
    """Get authentication headers with access token."""
    response = await client.post(
        "/api/v1/auth/login",
        json={
            "username": "testuser",
            "password": "password123"
        }
    )
    access_token = response.json()["data"]["access_token"]
    return {"Authorization": f"Bearer {access_token}"}


@pytest.fixture(scope="function")
async def test_channel(test_db):
    """Create a test channel."""
    from app.models.channel import Channel
    
    channel = Channel(
        name="Test Channel",
        category="entertainment",
        description="A test channel"
    )
    test_db.add(channel)
    await test_db.commit()
    await test_db.refresh(channel)
    return channel
