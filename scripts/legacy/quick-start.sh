#!/bin/bash
# Quick start script for AI Marketing Agent

echo "==== AI Marketing Agent Quick Start ===="
echo "This script will help you start the application components."
echo

# Check if any processes are already running
echo "Checking for existing processes..."
if pgrep -f "uvicorn app.main:app" > /dev/null; then
    echo "API is already running."
else
    echo "API is not running."
fi

if pgrep -f "npm run dev -- --port 3001" > /dev/null; then
    echo "Frontend is already running."
else
    echo "Frontend is not running."
fi

echo
echo "==== Starting Services ===="
echo

# Ask for confirmation
read -p "Start API with mock database? (y/n) " -n 1 -r
echo
if [[ $REPLY =~ ^[Yy]$ ]]; then
    echo "Starting API with mock database..."
    cd "$(dirname "$0")"
    pkill -f "uvicorn app.main:app" 2>/dev/null || true
    uvicorn app.main:app --host 127.0.0.1 --port 8088 --reload &
    echo "API starting on http://127.0.0.1:8088"
fi

echo
read -p "Start frontend development server? (y/n) " -n 1 -r
echo
if [[ $REPLY =~ ^[Yy]$ ]]; then
    echo "Starting frontend..."
    cd "$(dirname "$0")/frontend"
    pkill -f "npm run dev -- --port 3001" 2>/dev/null || true
    npm run dev -- --port 3001 --host 127.0.0.1 &
    echo "Frontend starting on http://127.0.0.1:3001"
fi

echo
echo "==== Application URLs ===="
echo "Frontend: http://localhost:3001"
echo "API: http://localhost:8088"
echo "API Documentation: http://localhost:8088/docs"
echo
echo "NOTE: The application uses MongoDB for data persistence."
echo "Ensure MongoDB is running: systemctl start mongod"
echo "You can access the component showcase at: http://localhost:3001/component-showcase"
echo 
echo "To stop the services: pkill -f 'uvicorn|npm run dev'"
