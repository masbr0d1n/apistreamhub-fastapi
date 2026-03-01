#!/bin/bash
# Quick test script for streaming endpoints
# Usage: ./test-streaming.sh

set -e

API_URL="${API_URL:-http://localhost:8000}"
USERNAME="${USERNAME:-testuser}"
PASSWORD="${PASSWORD:-testpass}"

echo "================================"
echo "🧪 Streaming API Test Script"
echo "================================"
echo ""
echo "API URL: $API_URL"
echo ""

# Colors
GREEN='\033[0;32m'
RED='\033[0;31m'
YELLOW='\033[1;33m'
NC='\033[0m'

# Step 1: Login
echo -n "1. Logging in... "
LOGIN_RESPONSE=$(curl -s -X POST "$API_URL/api/v1/auth/login" \
  -H "Content-Type: application/json" \
  -d "{\"username\":\"$USERNAME\",\"password\":\"$PASSWORD\"}")

TOKEN=$(echo $LOGIN_RESPONSE | jq -r '.data.access_token // empty')

if [ -z "$TOKEN" ] || [ "$TOKEN" = "null" ]; then
    echo -e "${RED}❌ FAIL${NC}"
    echo "Login failed. Response:"
    echo $LOGIN_RESPONSE
    exit 1
fi

echo -e "${GREEN}✅ PASS${NC}"
echo "   Token: ${TOKEN:0:20}..."
echo ""

# Step 2: Create test channel
echo -n "2. Creating test channel... "
CHANNEL_RESPONSE=$(curl -s -X POST "$API_URL/api/v1/channels/" \
  -H "Content-Type: application/json" \
  -H "Authorization: Bearer $TOKEN" \
  -d '{
    "name": "Test Streaming Channel",
    "category": "entertainment",
    "description": "Test channel for streaming control"
  }')

CHANNEL_ID=$(echo $CHANNEL_RESPONSE | jq -r '.data.id // empty')

if [ -z "$CHANNEL_ID" ] || [ "$CHANNEL_ID" = "null" ]; then
    echo -e "${RED}❌ FAIL${NC}"
    echo "Channel creation failed. Response:"
    echo $CHANNEL_RESPONSE
    exit 1
fi

echo -e "${GREEN}✅ PASS${NC}"
echo "   Channel ID: $CHANNEL_ID"
echo ""

# Step 3: Get initial status
echo -n "3. Getting initial status... "
STATUS_RESPONSE=$(curl -s -X GET "$API_URL/api/v1/streaming/channels/$CHANNEL_ID/status" \
  -H "Authorization: Bearer $TOKEN")

STATUS=$(echo $STATUS_RESPONSE | jq -r '.data.status // empty')

if [ "$STATUS" != "off-air" ]; then
    echo -e "${YELLOW}⚠️  UNEXPECTED${NC}"
    echo "   Expected: off-air, Got: $STATUS"
else
    echo -e "${GREEN}✅ PASS${NC}"
    echo "   Status: $STATUS"
fi
echo ""

# Step 4: Turn on channel
echo -n "4. Turning on channel... "
ON_RESPONSE=$(curl -s -X POST "$API_URL/api/v1/streaming/channels/$CHANNEL_ID/on-air" \
  -H "Authorization: Bearer $TOKEN")

ON_STATUS=$(echo $ON_RESPONSE | jq -r '.data.status // empty')

if [ "$ON_STATUS" != "on-air" ]; then
    echo -e "${RED}❌ FAIL${NC}"
    echo "Response:"
    echo $ON_RESPONSE
    exit 1
fi

echo -e "${GREEN}✅ PASS${NC}"
echo "   Status: $ON_STATUS"
echo "   Started at: $(echo $ON_RESPONSE | jq -r '.data.started_at')"
echo ""

# Step 5: Verify status changed
echo -n "5. Verifying status... "
VERIFY_RESPONSE=$(curl -s -X GET "$API_URL/api/v1/streaming/channels/$CHANNEL_ID/status" \
  -H "Authorization: Bearer $TOKEN")

VERIFY_STATUS=$(echo $VERIFY_RESPONSE | jq -r '.data.status // empty')

if [ "$VERIFY_STATUS" != "on-air" ]; then
    echo -e "${RED}❌ FAIL${NC}"
    echo "   Expected: on-air, Got: $VERIFY_STATUS"
    exit 1
fi

echo -e "${GREEN}✅ PASS${NC}"
echo "   Status: $VERIFY_STATUS"
echo ""

# Step 6: Turn off channel
echo -n "6. Turning off channel... "
OFF_RESPONSE=$(curl -s -X POST "$API_URL/api/v1/streaming/channels/$CHANNEL_ID/off-air" \
  -H "Authorization: Bearer $TOKEN")

OFF_STATUS=$(echo $OFF_RESPONSE | jq -r '.data.status // empty')

if [ "$OFF_STATUS" != "off-air" ]; then
    echo -e "${RED}❌ FAIL${NC}"
    echo "Response:"
    echo $OFF_RESPONSE
    exit 1
fi

echo -e "${GREEN}✅ PASS${NC}"
echo "   Status: $OFF_STATUS"
echo "   Stopped at: $(echo $OFF_RESPONSE | jq -r '.data.stopped_at')"
echo ""

# Step 7: Verify channel turned off
echo -n "7. Verifying channel turned off... "
FINAL_VERIFY=$(curl -s -X GET "$API_URL/api/v1/streaming/channels/$CHANNEL_ID/status" \
  -H "Authorization: Bearer $TOKEN")

FINAL_STATUS=$(echo $FINAL_VERIFY | jq -r '.data.status // empty')

if [ "$FINAL_STATUS" != "off-air" ]; then
    echo -e "${RED}❌ FAIL${NC}"
    echo "   Expected: off-air, Got: $FINAL_STATUS"
    exit 1
fi

echo -e "${GREEN}✅ PASS${NC}"
echo "   Status: $FINAL_STATUS"
echo ""

# Summary
echo "================================"
echo "📊 Test Results"
echo "================================"
echo -e "${GREEN}All tests passed! ✅${NC}"
echo ""
echo "Streaming control is working correctly."
echo ""
