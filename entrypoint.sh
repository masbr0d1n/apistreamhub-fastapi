#!/bin/bash
# Entrypoint script - MUST run as root first

# Create uploads directory as root
mkdir -p /app/uploads/videos/thumbnails

# Fix ownership
chown -R appuser:appuser /app/uploads

echo "✅ Uploads directory ready"

# Wait for database to be ready
echo "⏳ Waiting for database..."
for i in {1..30}; do
    if python -c "import socket; socket.create_connection(('apistreamhub-db', 5432), timeout=1)" 2>/dev/null; then
        echo "✅ Database is ready!"
        break
    fi
    echo "⏳ Waiting for database... attempt $i/30"
    sleep 2
done

# Drop to appuser and start application
echo "🚀 Starting StreamHub API..."
exec su appuser -c "uvicorn app.main:app --host 0.0.0.0 --port 8000 $@"
