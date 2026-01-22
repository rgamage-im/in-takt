#!/bin/bash
# RAG API Connection Test Script

echo "=== RAG API Connection Test ==="
echo ""

# Check if port 8000 is in use
echo "1. Checking if port 8000 is in use:"
if lsof -Pi :8000 -sTCP:LISTEN -t >/dev/null 2>&1 ; then
    echo "   ✓ Something is listening on port 8000"
    lsof -Pi :8000 -sTCP:LISTEN
else
    echo "   ✗ Nothing is listening on port 8000"
    echo "   → RAG API is not running"
fi

echo ""
echo "2. Checking Docker containers:"
docker ps --format "table {{.Names}}\t{{.Status}}\t{{.Ports}}" 2>/dev/null || echo "   Docker not available or no containers running"

echo ""
echo "3. Testing RAG API endpoints:"
echo "   Testing: http://localhost:8000/health"
RESPONSE=$(curl -s -w "\n%{http_code}" http://localhost:8000/health 2>/dev/null)
HTTP_CODE=$(echo "$RESPONSE" | tail -n1)
BODY=$(echo "$RESPONSE" | head -n-1)

if [ "$HTTP_CODE" = "000" ] || [ -z "$HTTP_CODE" ]; then
    echo "   ✗ Connection failed (RAG API not running)"
elif [ "$HTTP_CODE" = "200" ]; then
    echo "   ✓ HTTP $HTTP_CODE - Success"
    echo "   Response: $BODY"
elif [ "$HTTP_CODE" = "404" ]; then
    echo "   ✗ HTTP $HTTP_CODE - Endpoint not found"
    echo "   Response: $BODY"
else
    echo "   ⚠ HTTP $HTTP_CODE"
    echo "   Response: $BODY"
fi

echo ""
echo "4. Testing alternative root endpoint:"
echo "   Testing: http://localhost:8000/"
ROOT_RESPONSE=$(curl -s -w "\n%{http_code}" http://localhost:8000/ 2>/dev/null)
ROOT_CODE=$(echo "$ROOT_RESPONSE" | tail -n1)
ROOT_BODY=$(echo "$ROOT_RESPONSE" | head -n-1)

if [ "$ROOT_CODE" != "000" ] && [ -n "$ROOT_CODE" ]; then
    echo "   HTTP $ROOT_CODE"
    echo "   Response: ${ROOT_BODY:0:200}"
fi

echo ""
echo "5. RAG API Configuration in Django:"
source venv/bin/activate
python -c "from django.conf import settings; print(f'   RAG_API_BASE_URL: {settings.RAG_API_BASE_URL}')" 2>/dev/null || echo "   Could not read Django settings"

echo ""
echo "=== Test Complete ==="
