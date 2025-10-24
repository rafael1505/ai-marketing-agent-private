#!/bin/bash

# Test script for API endpoints
# This script tests the API endpoints for the simple_test_api.py server

# Configuration
API_URL="http://127.0.0.1:8089"
TEST_CONFIG='{
  "id": "openai",
  "name": "OpenAI",
  "apiKey": "test-api-key-123",
  "selectedModel": "dall-e-3",
  "quality": "standard",
  "size": "1024x1024",
  "style": "vivid",
  "isActive": true
}'

echo "Testing API server at $API_URL"
echo "-----------------------------"

# Test root endpoint
echo "1. Testing root endpoint..."
curl -s $API_URL | jq
echo ""

# Test GET providers endpoint
echo "2. Testing GET providers endpoint..."
curl -s "$API_URL/api/v1/ai-providers" | jq
echo ""

# Test POST provider endpoint
echo "3. Testing POST provider endpoint..."
curl -s -X POST "$API_URL/api/v1/ai-providers" \
  -H "Content-Type: application/json" \
  -d "$TEST_CONFIG" | jq
echo ""

# Test GET providers again to verify update
echo "4. Testing GET providers after POST..."
curl -s "$API_URL/api/v1/ai-providers" | jq
echo ""

# Test duplicated path with proper URL encoding
echo "5. Testing duplicated path..."
curl -s "$API_URL/api/v1/api/v1/ai-providers" | jq
echo ""

# Test PUT provider endpoint
echo "6. Testing PUT provider endpoint..."
curl -s -X PUT "$API_URL/api/v1/ai-providers/openai" \
  -H "Content-Type: application/json" \
  -d "$TEST_CONFIG" | jq
echo ""

# Test validate endpoint
echo "7. Testing validate endpoint..."
curl -s -X POST "$API_URL/api/v1/ai-providers/validate" \
  -H "Content-Type: application/json" \
  -d '{"providerId": "openai", "apiKey": "test-api-key-123"}' | jq
echo ""

echo "Tests completed!"
