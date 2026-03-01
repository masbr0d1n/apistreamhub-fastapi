-- Add role and page_access columns to users table
-- Run this on the apistreamhub database

-- Add role column with default value
ALTER TABLE users ADD COLUMN IF NOT EXISTS role VARCHAR(20) DEFAULT 'user' NOT NULL;

-- Add page_access column (JSONB for PostgreSQL)
ALTER TABLE users ADD COLUMN IF NOT EXISTS page_access JSONB;

-- Update existing admin users to have admin role
UPDATE users SET role = 'admin' WHERE is_admin = true;

-- Add check constraint for valid roles
ALTER TABLE users ADD CONSTRAINT users_role_check 
  CHECK (role IN ('user', 'admin', 'superadmin'));

-- Create index on role for faster queries
CREATE INDEX IF NOT EXISTS idx_users_role ON users(role);

-- Update testuser2 to be admin for testing
UPDATE users SET role = 'admin' WHERE username = 'testuser2';

-- Verify changes
SELECT id, username, email, role, is_admin, is_active FROM users;
