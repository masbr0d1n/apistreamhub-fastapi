-- Migration: Change playlist_items.duration to NUMERIC for decimal precision
-- Date: 2026-03-02
-- Reason: Support precise duration values (e.g., 142.84s instead of rounded 143s)

-- Alter column to NUMERIC(10,2)
-- Allows up to 8 digits before decimal, 2 digits after
ALTER TABLE playlist_items
ALTER COLUMN duration TYPE NUMERIC(10,2);
