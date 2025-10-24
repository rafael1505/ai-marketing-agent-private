#!/bin/bash

# Complete rebuild and restart script for the AI Marketing Agent application
echo "🔄 Rebuilding and restarting the complete application..."

# Get the script directory
SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
cd "$SCRIPT_DIR"

# Stop any running processes (may need to adjust for your environment)
echo "🛑 Stopping any running services..."
pkill -f "uvicorn app.main" || true
pkill -f "npm run dev" || true

# Rebuild the frontend
echo "🏗️ Rebuilding frontend..."
cd "$SCRIPT_DIR/frontend"
rm -rf .next
rm -rf node_modules/.cache
npm ci
npm run build

# Start the backend
echo "🚀 Starting backend..."
cd "$SCRIPT_DIR"
uvicorn app.main:api_app --host 127.0.0.1 --port 8088 --reload &

# Wait for backend to start
echo "⏳ Waiting for backend to initialize..."
sleep 3

# Start the frontend
echo "🚀 Starting frontend on port 3001..."
cd "$SCRIPT_DIR/frontend"
npm run dev -- --port 3001 --host 127.0.0.1 &

echo "✅ Application is starting up!"
echo "   - Frontend: http://localhost:3001"
echo "   - Backend API: http://localhost:8088"
echo "   - Style Debugger: http://localhost:3001/style-debug"
echo ""
echo "Press Ctrl+C to stop all services"

# Wait for processes to finish (or be killed)
wait
