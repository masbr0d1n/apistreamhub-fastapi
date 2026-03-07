# Database Migration - Create Campaigns Table

## Migration SQL

```sql
-- Create campaign_status enum type
DO $$ BEGIN
    CREATE TYPE campaign_status AS ENUM ('draft', 'active', 'paused', 'completed');
EXCEPTION
    WHEN duplicate_object THEN null;
END $$;

-- Create campaigns table for Videotron campaign management
CREATE TABLE IF NOT EXISTS campaigns (
    id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    name VARCHAR(500) NOT NULL,
    description TEXT,
    screen_ids JSONB DEFAULT '[]',
    layout_ids JSONB DEFAULT '[]',
    status campaign_status DEFAULT 'draft' NOT NULL,
    start_date TIMESTAMP WITH TIME ZONE,
    end_date TIMESTAMP WITH TIME ZONE,
    created_by INTEGER REFERENCES users(id) ON DELETE SET NULL,
    created_at TIMESTAMP WITH TIME ZONE DEFAULT CURRENT_TIMESTAMP,
    updated_at TIMESTAMP WITH TIME ZONE DEFAULT CURRENT_TIMESTAMP
);

-- Create index on name for fast lookups
CREATE INDEX IF NOT EXISTS idx_campaigns_name ON campaigns(name);

-- Create index on status for filtering
CREATE INDEX IF NOT EXISTS idx_campaigns_status ON campaigns(status);

-- Create index on created_by for filtering by user
CREATE INDEX IF NOT EXISTS idx_campaigns_created_by ON campaigns(created_by);

-- Verify table
\d campaigns
```

## How to Run

### Option 1: Direct SQL (Development)

```bash
# Connect to database
docker exec -it apistreamhub-db psql -U user -d apistreamhub

# Run migration
\i /home/sysop/.openclaw/workspace/apistreamhub-fastapi/migrations/005_create_campaigns.sql
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
psql -U user -d apistreamhub -f migrations/005_create_campaigns.sql
```

## Verify Migration

```bash
# Check table structure
docker exec -it apistreamhub-db psql -U user -d apistreamhub -c "\d campaigns"
```

## Note

The Campaign model (`app/models/campaign.py`) will be created to match this schema. 
Tables will also be auto-created on app startup via `Base.metadata.create_all()`.
