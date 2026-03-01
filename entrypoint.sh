#!/bin/bash
# Entrypoint script - MUST run as root first

# Create uploads directory as root
mkdir -p /app/uploads/videos/thumbnails

# Fix ownership
chown -R appuser:appuser /app/uploads

# Drop to appuser and start application
echo "✅ Uploads directory ready"
exec su appuser -c "uvicorn app.main:app --host 0.0.0.0 --port 8000 $@"
