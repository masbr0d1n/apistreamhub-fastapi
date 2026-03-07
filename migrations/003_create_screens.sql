# Database Migration - Create Screens and Screen Groups Tables

## Migration SQL

```sql
-- Create screens table for Videotron device management
CREATE TABLE IF NOT EXISTS screens (
    id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    device_id VARCHAR(255) UNIQUE NOT NULL,
    name VARCHAR(500) NOT NULL,
    location VARCHAR(500),
    resolution VARCHAR(50),
    status VARCHAR(20) DEFAULT 'offline' CHECK (status IN ('online', 'offline', 'maintenance')),
    last_heartbeat TIMESTAMP WITH TIME ZONE,
    api_key VARCHAR(255) UNIQUE,
    created_at TIMESTAMP WITH TIME ZONE DEFAULT CURRENT_TIMESTAMP,
    updated_at TIMESTAMP WITH TIME ZONE DEFAULT CURRENT_TIMESTAMP
);

-- Create index on device_id for fast lookups
CREATE INDEX IF NOT EXISTS idx_screens_device_id ON screens(device_id);

-- Create index on status for filtering
CREATE INDEX IF NOT EXISTS idx_screens_status ON screens(status);

-- Create screen_groups table for grouping screens
CREATE TABLE IF NOT EXISTS screen_groups (
    id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    name VARCHAR(500) NOT NULL,
    created_at TIMESTAMP WITH TIME ZONE DEFAULT CURRENT_TIMESTAMP
);

-- Create screen_group_items junction table for many-to-many relationship
CREATE TABLE IF NOT EXISTS screen_group_items (
    id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    group_id UUID NOT NULL REFERENCES screen_groups(id) ON DELETE CASCADE,
    screen_id UUID NOT NULL REFERENCES screens(id) ON DELETE CASCADE,
    created_at TIMESTAMP WITH TIME ZONE DEFAULT CURRENT_TIMESTAMP,
    UNIQUE(group_id, screen_id)
);

-- Create indexes for foreign keys
CREATE INDEX IF NOT EXISTS idx_screen_group_items_group_id ON screen_group_items(group_id);
CREATE INDEX IF NOT EXISTS idx_screen_group_items_screen_id ON screen_group_items(screen_id);

-- Verify tables
\d screens
\d screen_groups
\d screen_group_items
```

## How to Run

### Option 1: Direct SQL (Development)

```bash
# Connect to database
docker exec -it apistreamhub-db psql -U user -d apistreamhub

# Run migration
\i /home/sysop/.openclaw/workspace/apistreamhub-fastapi/migrations/003_create_screens.sql
```

### Option 2: Using docker exec

```bash
docker exec -i apistreamhub-db psql -U user -d apistreamhub << 'EOF'
-- Paste SQL from above
EOF
```

### Option 3: Run via script

```bash
cd /home/sysop/.openclaw/workspace/apistreamhub-fastapi
psql -U user -d apistreamhub -f migrations/003_create_screens.sql
```

## Verify Migration

```bash
# Check table structure
docker exec -it apistreamhub-db psql -U user -d apistreamhub -c "\d screens"
docker exec -it apistreamhub-db psql -U user -d apistreamhub -c "\d screen_groups"
docker exec -it apistreamhub-db psql -U user -d apistreamhub -c "\d screen_group_items"
```

## Note

The Screen and ScreenGroup models (`app/models/screen.py`, `app/models/screen_group.py`) 
will be created to match this schema. Tables will also be auto-created on app startup 
via `Base.metadata.create_all()`.
