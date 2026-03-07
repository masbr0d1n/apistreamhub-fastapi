# Database Migration - Create Layouts Table

## Migration SQL

```sql
-- Create layouts table for Videotron layout management
CREATE TABLE IF NOT EXISTS layouts (
    id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    name VARCHAR(500) NOT NULL,
    canvas_config JSONB,
    layers JSONB,
    created_by INTEGER REFERENCES users(id) ON DELETE SET NULL,
    created_at TIMESTAMP WITH TIME ZONE DEFAULT CURRENT_TIMESTAMP,
    updated_at TIMESTAMP WITH TIME ZONE DEFAULT CURRENT_TIMESTAMP
);

-- Create index on name for fast lookups
CREATE INDEX IF NOT EXISTS idx_layouts_name ON layouts(name);

-- Create index on created_by for filtering by user
CREATE INDEX IF NOT EXISTS idx_layouts_created_by ON layouts(created_by);

-- Verify table
\d layouts
```

## How to Run

### Option 1: Direct SQL (Development)

```bash
# Connect to database
docker exec -it apistreamhub-db psql -U user -d apistreamhub

# Run migration
\i /home/sysop/.openclaw/workspace/apistreamhub-fastapi/migrations/004_create_layouts.sql
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
psql -U user -d apistreamhub -f migrations/004_create_layouts.sql
```

## Verify Migration

```bash
# Check table structure
docker exec -it apistreamhub-db psql -U user -d apistreamhub -c "\d layouts"
```

## Note

The Layout model (`app/models/layout.py`) will be created to match this schema. 
Tables will also be auto-created on app startup via `Base.metadata.create_all()`.
