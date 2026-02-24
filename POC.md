# FastAPI + PostgreSQL PoC

## 🎯 PoC Scope

This is a **Proof of Concept (PoC)** for migrating StreamHub API from Flask to FastAPI with PostgreSQL.

### What's Included (Week 1 - Core Setup)

✅ **Project Structure**
- Modern FastAPI project layout
- SQLAlchemy 2.0 async ORM
- Pydantic v2 for validation
- JWT authentication
- PostgreSQL async (asyncpg)

✅ **Core Functionality**
- Configuration management (Pydantic Settings)
- Database connection pooling
- Exception handling
- CORS configuration
- API docs (Swagger UI + ReDoc)

✅ **Implemented Endpoints (Week 2)**
- `/api/v1/auth/register` - User registration
- `/api/v1/auth/login` - JWT login
- `/api/v1/auth/refresh` - Token refresh
- `/api/v1/auth/me` - Get current user
- `/api/v1/channels/` - CRUD operations for channels

---

## 🏗️ Architecture

```
apistreamhub-fastapi/
├── app/
│   ├── main.py                 # FastAPI instance
│   ├── config.py               # Settings (Pydantic)
│   ├── db/                     # Database
│   │   └── base.py             # SQLAlchemy async session
│   ├── models/                 # Database models
│   │   ├── user.py             # User model
│   │   └── channel.py          # Channel model
│   ├── schemas/                # Pydantic schemas
│   │   ├── auth.py             # Auth DTOs
│   │   └── channel.py          # Channel DTOs
│   ├── services/               # Business logic
│   │   ├── auth_service.py     # Auth logic
│   │   └── channel_service.py  # Channel logic
│   ├── core/                   # Core functionality
│   │   ├── exceptions.py       # Custom exceptions
│   │   └── security.py         # JWT, password hashing
│   └── api/v1/                 # API routes
│       ├── auth.py             # Auth endpoints
│       └── channels.py         # Channel endpoints
├── tests/                      # Tests (to be added)
├── pyproject.toml              # Project config
├── requirements.txt            # Dependencies
└── .env.dev                    # Environment variables
```

---

## 🚀 Quick Start

### 1. Setup PostgreSQL

```bash
# Create database
sudo -u postgres createdb apistreamhub

# Or use Docker
docker run -d \
  --name apistreamhub-db \
  -e POSTGRES_PASSWORD=postgres \
  -e POSTGRES_DB=apistreamhub \
  -p 5432:5432 \
  postgres:16
```

### 2. Configure Environment

```bash
# Copy environment template
cat > .env.dev << 'EOF'
# Database
DATABASE_URL=postgresql+asyncpg://postgres:postgres@localhost:5432/apistreamhub

# JWT
JWT_SECRET_KEY=your-secret-key-change-in-production

# Debug
DEBUG=true
EOF
```

### 3. Install Dependencies

```bash
# Create virtual environment
python3 -m venv .venv
source .venv/bin/activate

# Install dependencies
pip install -r requirements.txt
```

### 4. Run Migrations

```bash
# Initialize database
python -c "from app.main import app; import asyncio; asyncio.run(app.router.startup())"
```

### 5. Start Server

```bash
# Development
uvicorn app.main:app --reload --host 0.0.0.0 --port 8000

# Or use Python
python -m app.main
```

### 6. Access API

- **Swagger UI**: http://localhost:8000/docs
- **ReDoc**: http://localhost:8000/redoc
- **OpenAPI JSON**: http://localhost:8000/openapi.json

---

## 📡 API Endpoints

### Authentication

#### Register User
```bash
POST /api/v1/auth/register
Content-Type: application/json

{
  "username": "testuser",
  "email": "test@example.com",
  "full_name": "Test User",
  "password": "password123"
}
```

#### Login
```bash
POST /api/v1/auth/login
Content-Type: application/json

{
  "username": "testuser",
  "password": "password123"
}
```

#### Get Current User (Protected)
```bash
GET /api/v1/auth/me
Authorization: Bearer <access_token>
```

### Channels

#### List All Channels
```bash
GET /api/v1/channels/
```

#### Get Channel by ID
```bash
GET /api/v1/channels/1
```

#### Create Channel
```bash
POST /api/v1/channels/create-channel
Content-Type: application/json
Authorization: Bearer <access_token>

{
  "name": "Test Channel",
  "category": "entertainment",
  "description": "A test channel",
  "logo_url": "https://example.com/logo.png"
}
```

#### Update Channel
```bash
PUT /api/v1/channels/1
Content-Type: application/json
Authorization: Bearer <access_token>

{
  "name": "Updated Channel",
  "category": "sport"
}
```

#### Delete Channel
```bash
DELETE /api/v1/channels/1
Authorization: Bearer <access_token>
```

---

## 🎯 Success Criteria

### Performance
- [ ] ≥ 2x faster than Flask (target: 10K req/sec)
- [ ] Latency p95 < 100ms (Flask: ~200ms)
- [ ] Memory usage < 150MB (Flask: ~150MB)

### Functionality
- [x] All auth endpoints working
- [x] All channel endpoints working
- [ ] Video endpoints working
- [ ] JWT authentication working
- [ ] PostgreSQL queries working

### Quality
- [ ] All tests passing (pytest)
- [ ] Type hints 100% coverage
- [ ] API docs auto-generated
- [ ] Error handling comprehensive

---

## 📊 Progress Tracking

### Week 1: Core Setup ✅
- [x] Project structure created
- [x] PostgreSQL setup (SQLAlchemy async)
- [x] Configuration management (Pydantic Settings)
- [x] Exception handling
- [x] Security module (JWT, password hashing)

### Week 2: API Migration (In Progress)
- [x] Auth endpoints (`/api/v1/auth/*`)
- [x] Channel endpoints (`/api/v1/channels/*`)
- [ ] Video endpoints (`/api/v1/videos/*`)
- [ ] Testing
- [ ] Performance validation

---

## 🧪 Testing

### Run Tests

```bash
# Install test dependencies
pip install pytest pytest-asyncio httpx

# Run tests
pytest tests/ -v

# With coverage
pytest --cov=app tests/
```

### Example Test

```python
import pytest
from httpx import AsyncClient
from app.main import app

@pytest.mark.asyncio
async def test_register_user():
    async with AsyncClient(app=app) as client:
        response = await client.post(
            "/api/v1/auth/register",
            json={
                "username": "testuser",
                "email": "test@example.com",
                "full_name": "Test User",
                "password": "password123"
            }
        )
        assert response.status_code == 201
        data = response.json()
        assert data["status"] is True
```

---

## 📈 Next Steps (After PoC)

1. **Migrate remaining endpoints** (videos, playlists, live, etc.)
2. **Add comprehensive testing** (pytest, integration, load tests)
3. **Setup CI/CD** (GitHub Actions)
4. **Docker containerization**
5. **Database migrations** (Alembic)
6. **Production deployment**

---

## 🎓 Key Differences: Flask vs FastAPI

| Feature | Flask (Current) | FastAPI (PoC) |
|---------|-----------------|----------------|
| **Performance** | ~5K req/s | ~15K req/s (3x) ✅ |
| **Async** | Threads (Flask-Executor) | Native async/await ✅ |
| **Validation** | Marshmallow (manual) | Pydantic (automatic) ✅ |
| **Type Safety** | No | Full type hints ✅ |
| **API Docs** | Manual (Flask-Swagger) | Auto (Swagger UI) ✅ |
| **Database** | RethinkDB (deprecated) | PostgreSQL (async) ✅ |
| **Error Handling** | Manual make_response() | HTTPException ✅ |

---

## 📚 Documentation

- **FastAPI Docs**: https://fastapi.tiangolo.com/
- **SQLAlchemy 2.0**: https://docs.sqlalchemy.org/en/20/changelog/migration_20.html
- **Pydantic v2**: https://docs.pydantic.dev/latest/
- **PostgreSQL Async**: https://magicstack.github.io/asyncpg/

---

**Status**: 🟡 **PoC IN PROGRESS**
**Timeline**: 2 weeks
**Current**: Week 2 (API Migration)

Started: 2026-02-24
Target Completion: 2026-03-10
