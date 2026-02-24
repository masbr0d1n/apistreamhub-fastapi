"""
Pytest configuration and fixtures.
"""
import asyncio
import pytest
from typing import AsyncGenerator, Generator
from httpx import AsyncClient, ASGITransport
from sqlalchemy.ext.asyncio import AsyncSession, create_async_engine, async_sessionmaker
from sqlalchemy.pool import StaticPool

from app.main import app
from app.db.base import Base, get_db
from app.models.user import User
from app.models.channel import Channel
from app.models.video import Video
from app.core.security import get_password_hash


# Test database URL
TEST_DATABASE_URL = "sqlite+aiosqlite:///:memory:"


# Create test engine
test_engine = create_async_engine(
    TEST_DATABASE_URL,
    connect_args={"check_same_thread": False},
    poolclass=StaticPool,
)

TestSessionLocal = async_sessionmaker(
    autocommit=False,
    autoflush=False,
    bind=test_engine,
    class_=AsyncSession,
    expire_on_commit=False,  # Important: Prevent lazy loading after commit
)


@pytest.fixture(scope="session")
def event_loop() -> Generator:
    """Create event loop for async tests."""
    loop = asyncio.get_event_loop_policy().new_event_loop()
    yield loop
    loop.close()


@pytest.fixture(scope="function")
async def db_session() -> AsyncGenerator[AsyncSession, None]:
    """Create test database session."""
    async with test_engine.begin() as conn:
        await conn.run_sync(Base.metadata.create_all)
    
    async with TestSessionLocal() as session:
        yield session
    
    async with test_engine.begin() as conn:
        await conn.run_sync(Base.metadata.drop_all)


@pytest.fixture(scope="function")
async def client(db_session: AsyncSession) -> AsyncGenerator[AsyncClient, None]:
    """Create test client."""
    async def override_get_db():
        yield db_session
    
    app.dependency_overrides[get_db] = override_get_db
    
    async with AsyncClient(
        transport=ASGITransport(app=app),
        base_url="http://test"
    ) as ac:
        yield ac
    
    app.dependency_overrides.clear()


@pytest.fixture
async def test_user(db_session: AsyncSession) -> User:
    """Create test user."""
    user = User(
        username="testuser",
        email="test@example.com",
        full_name="Test User",
        hashed_password=get_password_hash("password123"),
        is_active=True,
        is_admin=False
    )
    db_session.add(user)
    await db_session.commit()
    await db_session.refresh(user)  # Ensure all attributes are loaded
    return user


@pytest.fixture
async def test_channel(db_session: AsyncSession) -> Channel:
    """Create test channel."""
    channel = Channel(
        name="Test Channel",
        category="entertainment",
        description="A test channel"
    )
    db_session.add(channel)
    await db_session.commit()
    await db_session.refresh(channel)
    return channel


@pytest.fixture
async def test_video(db_session: AsyncSession, test_channel: Channel) -> Video:
    """Create test video."""
    video = Video(
        title="Test Video",
        description="A test video",
        youtube_id="dQw4w9WgXcQ",
        channel_id=test_channel.id,
        duration=213,
        view_count=1000
    )
    db_session.add(video)
    await db_session.commit()
    await db_session.refresh(video)
    return video


@pytest.fixture
async def auth_headers(client: AsyncClient, test_user: User) -> dict:
    """Get authentication headers."""
    # Login to get token
    response = await client.post(
        "/api/v1/auth/login",
        json={
            "username": "testuser",
            "password": "password123"
        }
    )
    data = response.json()
    token = data["data"]["access_token"]
    return {"Authorization": f"Bearer {token}"}
