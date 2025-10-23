#!/bin/bash

# MCPO Test Script for KeikenV
# Tests the MCP-to-OpenAPI proxy functionality

set -euo pipefail

MCPO_URL="http://localhost:8940"
API_KEY="keiken-mcpo-secret-2024"
AUTH_HEADER="Authorization: Bearer $API_KEY"

echo "🧪 Testing MCPO (MCP-to-OpenAPI Proxy) Integration"
echo "=================================================="

# Test 1: Check root documentation
echo "📚 Test 1: Checking main documentation endpoint..."
if curl -s -H "$AUTH_HEADER" "$MCPO_URL/docs" | grep -q "MCP OpenAPI Proxy"; then
    echo "✅ Main docs accessible"
else
    echo "❌ Main docs not accessible"
fi

# Test 2: Check individual MCP service docs
echo ""
echo "🔧 Test 2: Checking individual MCP service documentation..."

for service in memory time filesystem sqlite; do
    echo "  Testing $service service..."
    if curl -s -H "$AUTH_HEADER" "$MCPO_URL/$service/docs" | grep -q "Swagger UI"; then
        echo "  ✅ $service docs accessible"
    else
        echo "  ❌ $service docs not accessible"
    fi
done

# Test 3: Test memory service functionality
echo ""
echo "💾 Test 3: Testing memory service functionality..."

# Store a test value
echo "  Storing test data..."
STORE_RESPONSE=$(curl -s -X POST -H "$AUTH_HEADER" -H "Content-Type: application/json" \
    -d '{"key": "test_key", "value": "Hello KeikenV!"}' \
    "$MCPO_URL/memory/store" || echo "ERROR")

if [[ "$STORE_RESPONSE" != "ERROR" ]]; then
    echo "  ✅ Memory store operation successful"
    
    # Try to retrieve the value
    echo "  Retrieving test data..."
    RETRIEVE_RESPONSE=$(curl -s -H "$AUTH_HEADER" \
        "$MCPO_URL/memory/get?key=test_key" || echo "ERROR")
    
    if [[ "$RETRIEVE_RESPONSE" != "ERROR" ]]; then
        echo "  ✅ Memory retrieve operation successful"
        echo "  📊 Retrieved: $RETRIEVE_RESPONSE"
    else
        echo "  ❌ Memory retrieve operation failed"
    fi
else
    echo "  ❌ Memory store operation failed"
fi

# Test 4: Test time service
echo ""
echo "⏰ Test 4: Testing time service functionality..."

TIME_RESPONSE=$(curl -s -H "$AUTH_HEADER" "$MCPO_URL/time/current" || echo "ERROR")
if [[ "$TIME_RESPONSE" != "ERROR" ]]; then
    echo "  ✅ Time service accessible"
    echo "  🕒 Current time: $TIME_RESPONSE"
else
    echo "  ❌ Time service not accessible"
fi

# Test 5: Test filesystem service
echo ""
echo "📁 Test 5: Testing filesystem service functionality..."

FS_RESPONSE=$(curl -s -H "$AUTH_HEADER" "$MCPO_URL/filesystem/list?path=/tmp" || echo "ERROR")
if [[ "$FS_RESPONSE" != "ERROR" ]]; then
    echo "  ✅ Filesystem service accessible"
    echo "  📂 /tmp directory listing available"
else
    echo "  ❌ Filesystem service not accessible"
fi

# Test 6: Check health endpoint (if available)
echo ""
echo "🏥 Test 6: Checking service health..."

HEALTH_RESPONSE=$(curl -s "$MCPO_URL/health" 2>/dev/null || echo "Not available")
if [[ "$HEALTH_RESPONSE" != "Not available" && "$HEALTH_RESPONSE" != *"Not Found"* ]]; then
    echo "  ✅ Health endpoint accessible"
    echo "  💚 Health status: $HEALTH_RESPONSE"
else
    echo "  ℹ️  Dedicated health endpoint not available (this is normal)"
fi

echo ""
echo "🎉 MCPO Integration Test Complete!"
echo ""
echo "🌐 Available Endpoints:"
echo "  • Main API: $MCPO_URL/docs"
echo "  • Memory: $MCPO_URL/memory/docs"  
echo "  • Time: $MCPO_URL/time/docs"
echo "  • Filesystem: $MCPO_URL/filesystem/docs"
echo "  • SQLite: $MCPO_URL/sqlite/docs"
echo ""
echo "🔑 API Key: $API_KEY"
echo "📋 Use these endpoints in your KeikenV agents for MCP functionality!"