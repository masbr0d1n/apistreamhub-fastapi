-- Add video upload fields to videos table
-- Migration: add_video_upload_fields.sql
-- Date: 2026-02-28

-- Add video_url column (for uploaded video files)
ALTER TABLE videos ADD COLUMN IF NOT EXISTS video_url VARCHAR(500);

-- Add thumbnail_data column (base64 thumbnail data)
ALTER TABLE videos ADD COLUMN IF NOT EXISTS thumbnail_data TEXT;

-- Make youtube_id optional (for uploaded videos without YouTube ID)
ALTER TABLE videos ALTER COLUMN youtube_id DROP NOT NULL;

-- Add comments
COMMENT ON COLUMN videos.video_url IS 'URL to uploaded video file (e.g., /uploads/videos/{uuid}.mp4)';
COMMENT ON COLUMN videos.thumbnail_data IS 'Base64 encoded thumbnail image data';
