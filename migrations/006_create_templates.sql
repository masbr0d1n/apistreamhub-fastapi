# Database Migration - Create Templates Table

## Migration SQL

```sql
-- Create templates table for Videotron template management
CREATE TABLE IF NOT EXISTS templates (
    id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    name VARCHAR(500) NOT NULL,
    description TEXT,
    layout_id UUID REFERENCES layouts(id) ON DELETE SET NULL,
    thumbnail TEXT,
    category VARCHAR(100),
    created_by INTEGER REFERENCES users(id) ON DELETE SET NULL,
    created_at TIMESTAMP WITH TIME ZONE DEFAULT CURRENT_TIMESTAMP,
    updated_at TIMESTAMP WITH TIME ZONE DEFAULT CURRENT_TIMESTAMP
);

-- Create index on name for fast lookups
CREATE INDEX IF NOT EXISTS idx_templates_name ON templates(name);

-- Create index on category for filtering
CREATE INDEX IF NOT EXISTS idx_templates_category ON templates(category);

-- Create index on created_by for filtering by user
CREATE INDEX IF NOT EXISTS idx_templates_created_by ON templates(created_by);

-- Create index on layout_id for filtering
CREATE INDEX IF NOT EXISTS idx_templates_layout_id ON templates(layout_id);

-- Verify table
\d templates
```

## How to Run

### Option 1: Direct SQL (Development)

```bash
# Connect to database
docker exec -it apistreamhub-db psql -U user -d apistreamhub

# Run migration
\i /home/sysop/.openclaw/workspace/apistreamhub-fastapi/migrations/006_create_templates.sql
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
psql -U user -d apistreamhub -f migrations/006_create_templates.sql
```

## Verify Migration

```bash
# Check table structure
docker exec -it apistreamhub-db psql -U user -d apistreamhub -c "\d templates"
```

## Note

The Template model (`app/models/template.py`) will be created to match this schema. 
Tables will also be auto-created on app startup via `Base.metadata.create_all()`.
