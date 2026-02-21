#!/bin/bash
echo "Stopping any existing API servers..."
pkill -f "uvicorn app.main:api_app" || true
sleep 2
echo "Starting new API server..."
cd "$(dirname "$0")"
uvicorn app.main:api_app --host 127.0.0.1 --port 8088 --reload
