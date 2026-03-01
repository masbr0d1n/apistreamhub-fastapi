# Database Initialization Script
# Ensures users and roles are never lost when recreating database

#!/bin/bash

DB_CONTAINER=${1:-apistreamhub-db}
DB_USER=${2:-postgres}
DB_NAME=${3:-apistreamhub}

echo "=== Initializing StreamHub Database ==="
echo "Container: $DB_CONTAINER"
echo "Database: $DB_NAME"
echo ""

# Wait for database to be ready
echo "Waiting for database to be ready..."
until docker exec $DB_CONTAINER pg_isready -U $DB_USER 2>/dev/null; do
  echo "Database not ready, waiting..."
  sleep 2
done
echo "✓ Database is ready"
echo ""

# Create tables if not exist
echo "Creating tables..."
docker exec -i $DB_CONTAINER psql -U $DB_USER -d $DB_NAME << 'EOF'
-- Users table
CREATE TABLE IF NOT EXISTS users (
    id SERIAL PRIMARY KEY,
    username VARCHAR(100) NOT NULL UNIQUE,
    email VARCHAR(255) NOT NULL UNIQUE,
    hashed_password VARCHAR(255) NOT NULL,
    full_name VARCHAR(255) NOT NULL,
    is_active BOOLEAN DEFAULT true NOT NULL,
    is_admin BOOLEAN DEFAULT false NOT NULL,
    role VARCHAR(50) DEFAULT 'USER' NOT NULL,
    page_access JSON,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP NOT NULL,
    last_login TIMESTAMP
);

-- Channels table
CREATE TABLE IF NOT EXISTS channels (
    id SERIAL PRIMARY KEY,
    name VARCHAR(255) NOT NULL,
    category VARCHAR(100) NOT NULL,
    description TEXT,
    thumbnail_url VARCHAR(500),
    is_active BOOLEAN DEFAULT true NOT NULL,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP NOT NULL,
    updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP NOT NULL
);

-- Videos table
CREATE TABLE IF NOT EXISTS videos (
    id SERIAL PRIMARY KEY,
    title VARCHAR(500) NOT NULL,
    description TEXT,
    youtube_id VARCHAR(255),
    channel_id INTEGER NOT NULL,
    video_url VARCHAR(500),
    thumbnail_url VARCHAR(500),
    thumbnail_data TEXT,
    duration NUMERIC,
    view_count INTEGER DEFAULT 0,
    is_live BOOLEAN DEFAULT false,
    is_active BOOLEAN DEFAULT true,
    width INTEGER,
    height INTEGER,
    fps FLOAT,
    video_codec VARCHAR(50),
    video_bitrate BIGINT,
    audio_codec VARCHAR(50),
    audio_bitrate BIGINT,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP NOT NULL,
    updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP NOT NULL
);

-- Playlists table
CREATE TABLE IF NOT EXISTS playlists (
    id SERIAL PRIMARY KEY,
    name VARCHAR(255) NOT NULL,
    description TEXT,
    user_id INTEGER NOT NULL,
    is_active BOOLEAN DEFAULT true NOT NULL,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP NOT NULL,
    updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP NOT NULL
);

-- Playlist videos table
CREATE TABLE IF NOT EXISTS playlist_videos (
    id SERIAL PRIMARY KEY,
    playlist_id INTEGER NOT NULL,
    video_id INTEGER NOT NULL,
    position INTEGER NOT NULL,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP NOT NULL,
    UNIQUE(playlist_id, video_id)
);

-- Role presets table
CREATE TABLE IF NOT EXISTS role_presets (
    id SERIAL PRIMARY KEY,
    name VARCHAR(100) NOT NULL UNIQUE,
    description TEXT,
    permissions JSON NOT NULL,
    is_active BOOLEAN DEFAULT true NOT NULL,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP NOT NULL
);
EOF
echo "✓ Tables created"
echo ""

# Check if admin user exists
ADMIN_EXISTS=$(docker exec $DB_CONTAINER psql -U $DB_USER -d $DB_NAME -tAc "SELECT COUNT(*) FROM users WHERE username = 'admin';")

if [ "$ADMIN_EXISTS" -eq "0" ]; then
    echo "Admin user does not exist, creating..."
    
    # Create admin user via API after backend starts
    # For now, create placeholder with known hash (password: admin123)
    docker exec -i $DB_CONTAINER psql -U $DB_USER -d $DB_NAME << 'EOF'
INSERT INTO users (username, email, full_name, hashed_password, is_active, is_admin, role)
VALUES (
    'admin',
    'admin@streamhub.com',
    'Administrator',
    '$2b$12$LQv3c1yqBWVHxkd0LHAkCOYz6TtxMQJqhN8/LewY5NU9xKZk6qHGy',
    true,
    true,
    'SUPERADMIN'
);
EOF
    echo "✓ Admin user created (username: admin, password: admin123)"
else
    echo "✓ Admin user already exists"
fi
echo ""

# Check if channels exist
CHANNEL_COUNT=$(docker exec $DB_CONTAINER psql -U $DB_USER -d $DB_NAME -tAc "SELECT COUNT(*) FROM channels;")

if [ "$CHANNEL_COUNT" -eq "0" ]; then
    echo "No channels found, creating default channels..."
    docker exec -i $DB_CONTAINER psql -U $DB_USER -d $DB_NAME << 'EOF'
INSERT INTO channels (name, category, description, is_active) VALUES
('Entertainment', 'entertainment', 'Entertainment videos', true),
('Sport', 'sport', 'Sport videos', true),
('Kids', 'kids', 'Kids content', true),
('Knowledge', 'knowledge', 'Knowledge videos', true),
('Gaming', 'gaming', 'Gaming videos', true);
EOF
    echo "✓ Default channels created"
else
    echo "✓ Channels already exist ($CHANNEL_COUNT channels)"
fi
echo ""

# Check if role presets exist
ROLE_COUNT=$(docker exec $DB_CONTAINER psql -U $DB_USER -d $DB_NAME -tAc "SELECT COUNT(*) FROM role_presets;")

if [ "$ROLE_COUNT" -eq "0" ]; then
    echo "No role presets found, creating default roles..."
    docker exec -i $DB_CONTAINER psql -U $DB_USER -d $DB_NAME << 'EOF'
INSERT INTO role_presets (name, description, page_access, is_system, is_active)
VALUES
('Superadmin', 'Full system access', '{"all": true}', true, true),
('Admin', 'Administrative access', '{"dashboard": true, "content": true, "channels": true, "users": true}', true, true),
('Manager', 'Content manager access', '{"dashboard": true, "content": true, "channels": true}', true, true),
('Viewer', 'View only access', '{"dashboard": true}', true, true);
EOF
    echo "✓ Default role presets created"
else
    echo "✓ Role presets already exist ($ROLE_COUNT roles)"
fi
echo ""

# Summary
echo "=== Database Initialization Complete ==="
echo ""
echo "Users:"
docker exec $DB_CONTAINER psql -U $DB_USER -d $DB_NAME -c "SELECT id, username, role FROM users;"
echo ""
echo "Channels:"
docker exec $DB_CONTAINER psql -U $DB_USER -d $DB_NAME -c "SELECT id, name, category FROM channels;"
echo ""
echo "Role Presets:"
docker exec $DB_CONTAINER psql -U $DB_USER -d $DB_NAME -c "SELECT id, name FROM role_presets;"
echo ""
echo "✓ Database ready!"
