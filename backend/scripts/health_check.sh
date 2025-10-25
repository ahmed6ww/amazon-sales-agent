#!/bin/bash

# Health check script for post-deployment verification
# Usage: ./health_check.sh [URL]

URL="${1:-http://localhost:8000}"

echo "🏥 Checking health of: $URL"
echo "==============================================="

# Check /health endpoint
echo "Testing /health endpoint..."
HEALTH_RESPONSE=$(curl -s -o /dev/null -w "%{http_code}" "$URL/health")

if [ "$HEALTH_RESPONSE" = "200" ]; then
    echo "✅ Health check passed (200 OK)"
else
    echo "❌ Health check failed (HTTP $HEALTH_RESPONSE)"
    exit 1
fi

# Check root endpoint
echo "Testing root endpoint..."
ROOT_RESPONSE=$(curl -s -o /dev/null -w "%{http_code}" "$URL/")

if [ "$ROOT_RESPONSE" = "200" ]; then
    echo "✅ Root endpoint OK (200)"
else
    echo "⚠️ Root endpoint returned HTTP $ROOT_RESPONSE"
fi

echo "==============================================="
echo "✅ All health checks passed!"
echo "==============================================="

# Get actual health response
echo ""
echo "Health endpoint response:"
curl -s "$URL/health" | python -m json.tool || echo "(Could not format JSON)"

