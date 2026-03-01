#!/bin/bash

# Test Playlist API
TOKEN="eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9.eyJzdWIiOiI2IiwidXNlcm5hbWUiOiJzdXBlcmFkbWluIiwiZXhwIjoxNzcyNDIxMTU3fQ.m40QwFZXOf3cMuf8gAYV68LrXl-drNl5y8ItqFeYG7o"

echo "Testing GET /api/v1/playlists/1/"
echo "================================"
curl -s "http://192.168.8.117:8001/api/v1/playlists/1/" \
  -H "Authorization: Bearer $TOKEN" \
  -H "Content-Type: application/json" | python3 -m json.tool 2>/dev/null || curl -s "http://192.168.8.117:8001/api/v1/playlists/1/" -H "Authorization: Bearer $TOKEN"

echo ""
echo ""
echo "Testing GET /api/v1/playlists/"
echo "================================"
curl -s "http://192.168.8.117:8001/api/v1/playlists/" \
  -H "Authorization: Bearer $TOKEN" \
  -H "Content-Type: application/json" | python3 -m json.tool 2>/dev/null || curl -s "http://192.168.8.117:8001/api/v1/playlists/" -H "Authorization: Bearer $TOKEN"
