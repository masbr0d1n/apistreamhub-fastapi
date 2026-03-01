# Database Migration - Add Video Metadata Columns

## Migration SQL

```sql
-- Add video metadata columns to videos table
ALTER TABLE videos 
  ADD COLUMN IF NOT EXISTS description TEXT;

ALTER TABLE videos 
  ADD COLUMN IF NOT EXISTS thumbnail_data TEXT;

ALTER TABLE videos 
  ADD COLUMN IF NOT EXISTS width INTEGER;

ALTER TABLE videos 
  ADD COLUMN IF NOT EXISTS height INTEGER;

ALTER TABLE videos 
  ADD COLUMN IF NOT EXISTS fps FLOAT;

ALTER TABLE videos 
  ADD COLUMN IF NOT EXISTS video_codec VARCHAR(50);

ALTER TABLE videos 
  ADD COLUMN IF NOT EXISTS video_bitrate INTEGER;

ALTER TABLE videos 
  ADD COLUMN IF NOT EXISTS audio_codec VARCHAR(50);

ALTER TABLE videos 
  ADD COLUMN IF NOT EXISTS audio_bitrate INTEGER;

-- Verify columns
\d videos
```

## How to Run

### Option 1: Direct SQL (Production)

```bash
# Connect to database
docker exec -it apistreamhub-db psql -U streamhub -d streamhub

# Run migration
\i /path/to/migration.sql
```

### Option 2: Using docker exec

```bash
docker exec -i apistreamhub-db psql -U streamhub -d streamhub << 'EOF'
ALTER TABLE videos ADD COLUMN IF NOT EXISTS description TEXT;
ALTER TABLE videos ADD COLUMN IF NOT EXISTS thumbnail_data TEXT;
ALTER TABLE videos ADD COLUMN IF NOT EXISTS width INTEGER;
ALTER TABLE videos ADD COLUMN IF NOT EXISTS height INTEGER;
ALTER TABLE videos ADD COLUMN IF NOT EXISTS fps FLOAT;
ALTER TABLE videos ADD COLUMN IF NOT EXISTS video_codec VARCHAR(50);
ALTER TABLE videos ADD COLUMN IF NOT EXISTS video_bitrate INTEGER;
ALTER TABLE videos ADD COLUMN IF NOT EXISTS audio_codec VARCHAR(50);
ALTER TABLE videos ADD COLUMN IF NOT EXISTS audio_bitrate INTEGER;
EOF
```

### Option 3: Save and run SQL file

```bash
# Save migration
cat > /tmp/add_video_metadata.sql << 'EOF'
ALTER TABLE videos ADD COLUMN IF NOT EXISTS description TEXT;
ALTER TABLE videos ADD COLUMN IF NOT EXISTS thumbnail_data TEXT;
ALTER TABLE videos ADD COLUMN IF NOT EXISTS width INTEGER;
ALTER TABLE videos ADD COLUMN IF NOT EXISTS height INTEGER;
ALTER TABLE videos ADD COLUMN IF NOT EXISTS fps FLOAT;
ALTER TABLE videos ADD COLUMN IF NOT EXISTS video_codec VARCHAR(50);
ALTER TABLE videos ADD COLUMN IF NOT EXISTS video_bitrate INTEGER;
ALTER TABLE videos ADD COLUMN IF NOT EXISTS audio_codec VARCHAR(50);
ALTER TABLE videos ADD COLUMN IF NOT EXISTS audio_bitrate INTEGER;
EOF

# Run migration
docker exec -i apistreamhub-db psql -U streamhub -d streamhub < /tmp/add_video_metadata.sql
```

## Verify Migration

```bash
# Check table structure
docker exec -it apistreamhub-db psql -U streamhub -d streamhub -c "\d videos"

# Should see all new columns:
#  - description
#  - thumbnail_data
#  - width
#  - height
#  - fps
#  - video_codec
#  - video_bitrate
#  - audio_codec
#  - audio_bitrate
```

## Note

The Video model (`app/models/video.py`) already has all these fields defined.
This migration ensures the database schema matches the model.
