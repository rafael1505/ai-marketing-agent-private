#!/bin/bash

# Kill any existing uvicorn processes
echo "Stopping any running API servers..."
pkill -f "uvicorn app.main:app" || echo "No API server was running"

# Wait a moment for the process to fully terminate
sleep 2

# Start the API server
echo "Starting API server..."
cd "$(dirname "$0")"
python -m uvicorn app.main:app --host 127.0.0.1 --port 8088 --reload &

# Wait for server to start
sleep 5

# Test if server is responsive
echo "Testing API server..."
curl -s http://localhost:8088/ || echo "API server did not respond properly"
curl -s http://localhost:8088/api/v1/companies/active || echo "Companies endpoint did not respond"

echo "Restart complete"
