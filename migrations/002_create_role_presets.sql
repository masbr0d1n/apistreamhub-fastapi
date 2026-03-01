-- Create role_presets table
CREATE TABLE IF NOT EXISTS role_presets (
    id SERIAL PRIMARY KEY,
    name VARCHAR(100) UNIQUE NOT NULL,
    description VARCHAR(500),
    page_access JSONB NOT NULL DEFAULT '{}',
    is_system BOOLEAN DEFAULT FALSE,
    is_active BOOLEAN DEFAULT TRUE,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    created_by INTEGER
);

-- Create index on name
CREATE INDEX IF NOT EXISTS idx_role_presets_name ON role_presets(name);

-- Insert default Superadmin preset (system preset, cannot be deleted)
INSERT INTO role_presets (name, description, page_access, is_system)
VALUES (
    'Superadmin',
    'Full system access - all permissions granted',
    '{"dashboard": true, "channels": true, "videos": true, "composer": true, "users": true, "settings": true}',
    true
) ON CONFLICT (name) DO NOTHING;

-- Insert default Admin preset
INSERT INTO role_presets (name, description, page_access, is_system)
VALUES (
    'Admin',
    'Administrative access - manage channels, videos, and playlists',
    '{"dashboard": true, "channels": true, "videos": true, "composer": true, "users": false, "settings": true}',
    true
) ON CONFLICT (name) DO NOTHING;

-- Insert default User preset
INSERT INTO role_presets (name, description, page_access, is_system)
VALUES (
    'User',
    'Basic user access - view dashboard and videos',
    '{"dashboard": true, "channels": false, "videos": true, "composer": false, "users": false, "settings": false}',
    true
) ON CONFLICT (name) DO NOTHING;

-- Verify inserts
SELECT id, name, is_system, is_active FROM role_presets;
