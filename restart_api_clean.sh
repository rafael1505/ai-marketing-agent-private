#!/bin/bash

echo "Stopping any running API server processes..."
pkill -f "uvicorn app.main:api_app"
sleep 1

echo "Freeing ports..."
python port_utils.py free-all

echo "Cleaning any log files..."
> api_server.log
> api_server_8088.log
> api_server_8089.log

echo "Starting API server with clean state..."
uvicorn app.main:api_app --host 127.0.0.1 --port 8088 --reload > api_server_clean.log 2>&1 &

echo "API server started with clean state. Logs available in api_server_clean.log"
echo "Waiting for server to initialize..."
sleep 3

# Test if server is responding
if curl -s http://localhost:8088/api/v1/healthcheck; then
    echo "API server is running successfully!"
else
    echo "API server may have failed to start. Check api_server_clean.log for details."
fi
