# Migration Commands

## Quick Start

### 1. Apply Database Migration

```bash
# Option A: Using psql directly
psql -h localhost -U postgres -d apistreamhub -f migrations/add_streaming_fields.sql

# Option B: Using docker-compose exec
docker-compose exec -T postgres psql -U postgres -d apistreamhub <<EOF
ALTER TABLE channels 
ADD COLUMN IF NOT EXISTS is_on_air BOOLEAN DEFAULT FALSE NOT NULL;

ALTER TABLE channels 
ADD COLUMN IF NOT EXISTS started_streaming_at TIMESTAMP WITH TIME ZONE;

ALTER TABLE channels 
ADD COLUMN IF NOT EXISTS stopped_streaming_at TIMESTAMP WITH TIME ZONE;

CREATE INDEX IF NOT EXISTS idx_channels_is_on_air ON channels(is_on_air);
EOF
```

### 2. Restart FastAPI Backend

```bash
cd /home/sysop/.openclaw/workspace/apistreamhub-fastapi

# Stop existing containers
docker-compose down

# Rebuild and start
docker-compose up -d --build

# Check logs
docker-compose logs -f api
```

### 3. Run Tests

```bash
# All tests
pytest

# Streaming tests only
pytest tests/test_streaming.py -v

# With coverage
pytest tests/test_streaming.py --cov=app/services/streaming_service --cov-report=html
```

---

## Manual Migration Steps

If auto-migration fails:

```sql
-- Connect to database
docker-compose exec postgres psql -U postgres -d apistreamhub

-- Check current table structure
\d channels

-- Add columns one by one
ALTER TABLE channels ADD COLUMN is_on_air BOOLEAN DEFAULT FALSE NOT NULL;
ALTER TABLE channels ADD COLUMN started_streaming_at TIMESTAMP WITH TIME ZONE;
ALTER TABLE channels ADD COLUMN stopped_streaming_at TIMESTAMP WITH TIME ZONE;

-- Verify
SELECT column_name, data_type FROM information_schema.columns 
WHERE table_name = 'channels' 
ORDER BY ordinal_position;
```

---

## Troubleshooting

### Issue: Column already exists
```sql
-- Check if column exists
SELECT column_name FROM information_schema.columns 
WHERE table_name = 'channels' AND column_name = 'is_on_air';

-- If exists, skip migration
```

### Issue: Permission denied
```bash
# Run as postgres user
docker-compose exec -u postgres postgres psql -d apistreamhub
```

### Issue: Table doesn't exist
```bash
# Initialize database first
cd /home/sysop/.openclaw/workspace/apistreamhub-fastapi
python init_db.py
```

---

## Verification

After migration, verify with API:

```bash
# 1. Get auth token
TOKEN=$(curl -X POST "http://localhost:8000/api/v1/auth/login" \
  -H "Content-Type: application/json" \
  -d '{"username":"testuser","password":"testpass"}' \
  | jq -r '.data.access_token')

# 2. Create a test channel
CHANNEL_ID=$(curl -X POST "http://localhost:8000/api/v1/channels/" \
  -H "Content-Type: application/json" \
  -H "Authorization: Bearer $TOKEN" \
  -d '{
    "name": "Test Channel",
    "category": "entertainment",
    "description": "Test streaming"
  }' | jq -r '.data.id')

# 3. Turn on channel
curl -X POST "http://localhost:8000/api/v1/streaming/channels/$CHANNEL_ID/on-air" \
  -H "Authorization: Bearer $TOKEN"

# 4. Check status
curl -X GET "http://localhost:8000/api/v1/streaming/channels/$CHANNEL_ID/status" \
  -H "Authorization: Bearer $TOKEN"

# 5. Turn off channel
curl -X POST "http://localhost:8000/api/v1/streaming/channels/$CHANNEL_ID/off-air" \
  -H "Authorization: Bearer $TOKEN"
```

---

**Status:** ✅ Ready to apply
**Database:** PostgreSQL 16+
**API Version:** v1
