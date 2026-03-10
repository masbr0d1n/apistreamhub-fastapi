# Environment Configuration - PROJ-004

**Completed:** 2026-03-09  
**Priority:** High

---

## Summary

All hardcoded URLs and configuration values have been moved to environment variables. The application now supports multi-environment deployment (development, production) through Docker Compose profiles.

---

## Changes Made

### 1. Application Configuration (`app/config.py`)

**Before:**
- Hardcoded DATABASE_URL with localhost
- Hardcoded CORS_ORIGINS with localhost and 192.168.x.x addresses
- No RTMP streaming configuration

**After:**
- DATABASE_URL: Configurable via environment variable with description
- CORS_ORIGINS: Now accepts comma-separated string from environment, with sensible localhost defaults
- NEW: RTMP_STREAM_HOST and RTMP_STREAM_PORT for streaming URL configuration
- All configuration values properly documented with Field descriptions

### 2. Streaming Service (`app/services/streaming_service.py`)

**Before:**
```python
"stream_url": f"rtmp://localhost/live/{channel.name}"
```

**After:**
```python
from app.config import settings

"stream_url": f"rtmp://{settings.RTMP_STREAM_HOST}/live/{channel.name}"
```

### 3. Docker Compose Configuration

#### Main File (`docker-compose.yml`)
- All hardcoded values replaced with environment variable references
- Supports fallback defaults with `${VAR:-default}` syntax
- Database credentials configurable via DB_USER, DB_PASSWORD, DB_NAME
- RTMP streaming configuration exposed
- CORS origins configurable

#### Development Profile (`docker-compose.dev.yml`)
- Enables DEBUG mode
- Allows all localhost CORS origins
- Mounts app directory for hot-reloading
- Uses development-friendly ports (5434, 8001)

#### Production Profile (`docker-compose.prod.yml`)
- Disables DEBUG mode
- Restricts CORS to production domains only
- Removes database port exposure
- Adds resource limits and restart policies
- Uses production ports (5432, 8000)

### 4. Environment Files

#### `.env.example` (Updated)
Comprehensive documentation including:
- All configurable variables with descriptions
- Format examples for each variable
- Development vs production examples
- Docker Compose usage instructions
- Security warnings for sensitive values

---

## Configuration Variables

### Required Variables

| Variable | Description | Example |
|----------|-------------|---------|
| `JWT_SECRET_KEY` | JWT signing secret (min 32 chars) | `secrets.token_urlsafe(32)` |
| `DATABASE_URL` | PostgreSQL connection string | `postgresql+asyncpg://user:pass@host:5432/db` |

### Optional Variables (with defaults)

| Variable | Default | Description |
|----------|---------|-------------|
| `DEBUG` | `false` | Enable debug mode |
| `HOST` | `0.0.0.0` | Server bind address |
| `PORT` | `8000` | Server port |
| `CORS_ORIGINS` | localhost ports | Comma-separated allowed origins |
| `RTMP_STREAM_HOST` | `localhost` | RTMP server hostname |
| `RTMP_STREAM_PORT` | `1935` | RTMP server port |
| `UPLOAD_DIR` | `uploads/` | Upload directory path |
| `MAX_UPLOAD_SIZE` | `10485760` | Max upload size (bytes) |
| `TELEGRAM_BOT_TOKEN` | (empty) | Telegram bot token |
| `TELEGRAM_CHAT_ID` | (empty) | Telegram chat ID |

### Docker Compose Variables

| Variable | Default | Description |
|----------|---------|-------------|
| `DB_USER` | `postgres` | Database username |
| `DB_PASSWORD` | `postgres` | Database password |
| `DB_NAME` | `apistreamhub` | Database name |
| `DB_PORT` | `5434` | External database port |
| `API_PORT` | `8001` | External API port |

---

## Usage

### Development

1. Copy environment file:
```bash
cp .env.example .env.dev
```

2. Edit `.env.dev` with development values (JWT_SECRET_KEY required)

3. Start with development profile:
```bash
docker-compose -f docker-compose.yml -f docker-compose.dev.yml up
```

Access:
- API: http://localhost:8001
- Database: localhost:5434

### Production

1. Copy environment file:
```bash
cp .env.example .env
```

2. Edit `.env` with production values:
   - Generate strong JWT_SECRET_KEY
   - Set production DATABASE_URL
   - Configure CORS_ORIGINS for production domains
   - Set RTMP_STREAM_HOST to production streaming server

3. Start with production profile:
```bash
docker-compose -f docker-compose.yml -f docker-compose.prod.yml up -d
```

Access:
- API: http://your-domain:8000
- Database: Not exposed (internal only)

---

## Security Notes

### JWT Secret Key
Generate a strong secret key:
```bash
python -c 'import secrets; print(secrets.token_urlsafe(32))'
```

**Requirements:**
- Minimum 32 characters
- Never use default/example values in production
- Store securely (not in version control)

### Database Credentials
- Use strong passwords in production
- Never commit `.env` files to version control
- Consider using secrets management in production

### CORS Configuration
- Development: Include all localhost ports you're using
- Production: Only include your actual production domains
- Never use `*` in production

---

## Migration from Hardcoded Values

### Before (Hardcoded)
```python
# config.py
DATABASE_URL: str = "postgresql+asyncpg://user:password@localhost:5432/apistreamhub"
CORS_ORIGINS: List[str] = [
    "http://localhost:3000",
    "http://192.168.200.60:3000",  # Hardcoded IP
]
```

```python
# streaming_service.py
"stream_url": f"rtmp://localhost/live/{channel.name}"
```

### After (Environment Variables)
```python
# config.py
DATABASE_URL: str = Field(
    default="postgresql+asyncpg://user:password@localhost:5432/apistreamhub",
    description="PostgreSQL connection string"
)
CORS_ORIGINS: List[str] = Field(
    default=["http://localhost:3000", ...],
    description="Comma-separated list of allowed CORS origins"
)
RTMP_STREAM_HOST: str = Field(default="localhost")
```

```python
# streaming_service.py
from app.config import settings
"stream_url": f"rtmp://{settings.RTMP_STREAM_HOST}/live/{channel.name}"
```

---

## Testing

### Verify Configuration Loading

```bash
# Check if settings load correctly
docker-compose -f docker-compose.yml -f docker-compose.dev.yml config

# Test API health endpoint
curl http://localhost:8001/health
```

### Verify No Hardcoded URLs

```bash
# Should only show default values in config.py, no production IPs
grep -r "localhost" --include="*.py" app/
grep -r "192.168" --include="*.py" app/
```

---

## Acceptance Criteria

- [x] All hardcoded URLs moved to environment variables
- [x] `.env.example` created with comprehensive documentation
- [x] `docker-compose.yml` supports environment variables
- [x] `docker-compose.dev.yml` for development environment
- [x] `docker-compose.prod.yml` for production environment
- [x] RTMP streaming URLs configurable
- [x] CORS origins configurable via environment
- [x] Database credentials configurable
- [x] Application structure maintained (no breaking changes)

---

## Files Modified

1. `app/config.py` - Added Field descriptions, RTMP config, made CORS configurable
2. `app/services/streaming_service.py` - Use settings for RTMP URLs
3. `docker-compose.yml` - Environment variable support
4. `docker-compose.dev.yml` - NEW: Development overrides
5. `docker-compose.prod.yml` - NEW: Production overrides
6. `.env.example` - Comprehensive documentation and examples

---

## Next Steps

1. Update CI/CD pipelines to use new environment variables
2. Configure production secrets management
3. Update deployment documentation
4. Test with actual production values in staging environment
