-- Migration: Add streaming control fields to channels table
-- Date: 2026-02-25
-- Description: Adds is_on_air, started_streaming_at, and stopped_streaming_at columns

-- Add is_on_air column
ALTER TABLE channels 
ADD COLUMN IF NOT EXISTS is_on_air BOOLEAN DEFAULT FALSE NOT NULL;

-- Add started_streaming_at column
ALTER TABLE channels 
ADD COLUMN IF NOT EXISTS started_streaming_at TIMESTAMP WITH TIME ZONE;

-- Add stopped_streaming_at column
ALTER TABLE channels 
ADD COLUMN IF NOT EXISTS stopped_streaming_at TIMESTAMP WITH TIME ZONE;

-- Create index for faster queries
CREATE INDEX IF NOT EXISTS idx_channels_is_on_air ON channels(is_on_air);

-- Add comment
COMMENT ON COLUMN channels.is_on_air IS 'Whether the channel is currently on-air (streaming)';
COMMENT ON COLUMN channels.started_streaming_at IS 'Timestamp when the channel started streaming';
COMMENT ON COLUMN channels.stopped_streaming_at IS 'Timestamp when the channel stopped streaming';

-- Verification query (run this to check)
SELECT 
    column_name, 
    data_type, 
    column_default,
    is_nullable
FROM 
    information_schema.columns 
WHERE 
    table_name = 'channels' 
    AND column_name IN ('is_on_air', 'started_streaming_at', 'stopped_streaming_at');
