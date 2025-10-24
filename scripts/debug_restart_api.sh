#!/bin/bash

echo "API Server Restart and Test Script"
echo "=================================="

# Define variables
API_PORT=8088
API_HOST="localhost"
TEST_ENDPOINT="/api/v1/companies/active"

# Kill any existing uvicorn processes on the port
echo "Checking for processes using port $API_PORT..."
pid=$(lsof -t -i :$API_PORT)
if [ -n "$pid" ]; then
    echo "Found process(es) using port $API_PORT: $pid"
    echo "Stopping process(es)..."
    kill -9 $pid
    echo "Process(es) stopped."
else
    echo "No processes found using port $API_PORT."
fi

# Wait a moment to ensure port is free
sleep 2

# Start the API server
echo "Starting API server on port $API_PORT..."
cd "$(dirname "$0")"
python -m uvicorn app.main:app --host 127.0.0.1 --port $API_PORT --reload &

# Wait for server to start
echo "Waiting for server to start..."
for i in {1..10}; do
    sleep 1
    echo -n "."
done
echo ""

# Test if server is responsive
echo "Testing API server..."
response=$(curl -s -o /dev/null -w "%{http_code}" http://$API_HOST:$API_PORT/)
if [ "$response" == "000" ]; then
    echo "ERROR: API server did not respond"
    
    # Run the debug API server instead
    echo "Starting debug API server..."
    python debug_api_config.py &
    
    sleep 3
    echo "Testing debug API server..."
    curl -v http://$API_HOST:$API_PORT/api/v1/companies/active
else
    echo "API server responded with status code: $response"
    echo "Testing companies endpoint..."
    curl -v http://$API_HOST:$API_PORT/$TEST_ENDPOINT
fi

echo "Done"
