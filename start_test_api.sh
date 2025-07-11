#!/bin/bash

# Start the test API server
echo "Starting test API server on port 8089..."
python simple_test_api.py &
API_PID=$!
echo "API server started with PID: $API_PID"

# Wait a moment
sleep 2

# Check if the server is running
if ps -p $API_PID > /dev/null; then
    echo "API server is running."
    
    # Test the API
    echo "Testing API endpoint..."
    curl -s http://127.0.0.1:8089/ | jq || echo "curl failed, is the API running?"
    
    echo "Testing providers endpoint..."
    curl -s http://127.0.0.1:8089/api/v1/ai-providers | jq || echo "curl failed, is the API running?"
else
    echo "API server failed to start."
fi

echo "To stop the server: kill $API_PID"
