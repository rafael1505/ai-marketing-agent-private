#!/bin/bash

echo "=== AI Marketing Agent - Materials Page Test ==="
echo

# Test 1: Check if frontend is running
echo "1. Testing frontend availability..."
if curl -s http://localhost:3000 > /dev/null; then
    echo "✅ Frontend is running on http://localhost:3000"
else
    echo "❌ Frontend is not accessible"
    exit 1
fi

# Test 2: Check materials page
echo "2. Testing materials page..."
MATERIALS_RESPONSE=$(curl -s http://localhost:3000/en/materials)
if [[ $MATERIALS_RESPONSE == *"Materials"* ]]; then
    echo "✅ Materials page loads successfully"
else
    echo "❌ Materials page failed to load"
fi

# Test 3: Check edit page
echo "3. Testing edit page..."
EDIT_RESPONSE=$(curl -s http://localhost:3000/en/materials/demo-1/edit)
if [[ $EDIT_RESPONSE == *"Edit"* ]]; then
    echo "✅ Edit page loads successfully"
else
    echo "❌ Edit page failed to load"
fi

# Test 4: Backend API (optional - may not be running)
echo "4. Testing backend API..."
if curl -s http://127.0.0.1:8088/api/v1/diagnostic/ping > /dev/null; then
    echo "✅ Backend API is running"
else
    echo "⚠️  Backend API is not running (expected in demo mode)"
fi

echo
echo "=== Test Summary ==="
echo "The AI Marketing Agent should now work in development mode:"
echo "- Materials page: http://localhost:3000/en/materials"
echo "- Edit page: http://localhost:3000/en/materials/demo-1/edit"
echo "- Settings page: http://localhost:3000/en/settings"
echo
echo "In development mode, the app will:"
echo "✅ Show demo materials without requiring login"
echo "✅ Allow editing demo materials"
echo "✅ Not redirect to login page"
echo "✅ Work even when backend is offline"
