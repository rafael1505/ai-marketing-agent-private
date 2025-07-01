#!/bin/bash

# Quick Start Script for AI Marketing Agent
# This script ensures everything is started with the correct configuration

# Text formatting
BOLD='\033[1m'
GREEN='\033[0;32m'
YELLOW='\033[0;33m'
RED='\033[0;31m'
BLUE='\033[0;34m'
NC='\033[0m' # No Color

echo -e "${BOLD}===== AI Marketing Agent QuickStart =====${NC}"
echo "This script will start all required services with the correct configuration"
echo

# Function to check if port is in use
is_port_in_use() {
    if command -v lsof &> /dev/null; then
        lsof -i:$1 &> /dev/null
        return $?
    elif command -v netstat &> /dev/null; then
        netstat -tuln | grep -q ":$1 "
        return $?
    else
        # Fallback to direct check
        (echo > /dev/tcp/127.0.0.1/$1) &>/dev/null
        return $?
    fi
}

# Step 1: Kill any API server running on wrong port
if is_port_in_use 8089; then
    echo -e "${RED}⚠️ Detected API server running on incorrect port (8089)${NC}"
    echo "Stopping service on port 8089..."
    
    # Find and kill process on port 8089
    if command -v lsof &> /dev/null; then
        PID=$(lsof -t -i:8089 2>/dev/null)
        if [ -n "$PID" ]; then
            kill $PID
            sleep 2
        fi
    fi
fi

# Step 2: Check if correct API port is available
if is_port_in_use 8088; then
    echo -e "${YELLOW}⚠️ Port 8088 is already in use${NC}"
    echo "Checking if it's our API server..."
    
    API_STATUS=$(curl -s -o /dev/null -w "%{http_code}" "http://127.0.0.1:8088/api/v1/diagnostic/health" 2>/dev/null)
    if [[ "$API_STATUS" == "200" ]]; then
        echo -e "${GREEN}✓ API server is already running correctly on port 8088${NC}"
        API_RUNNING=true
    else
        echo -e "${RED}✗ Port 8088 is in use by another service${NC}"
        echo "Please free up port 8088 and try again"
        exit 1
    fi
else
    API_RUNNING=false
fi

# Step 3: Start API server if not running
if [ "$API_RUNNING" != "true" ]; then
    echo -e "${BLUE}Starting API server on port 8088...${NC}"
    
    cd "$(dirname "$0")"
    
    # Start API server as background process
    nohup uvicorn app.main:app --host 127.0.0.1 --port 8088 --reload > api_server_8088.log 2>&1 &
    API_PID=$!
    
    echo "Started API server with PID: $API_PID"
    
    # Wait for API server to start
    echo "Waiting for API server to start..."
    for i in {1..10}; do
        sleep 1
        echo -n "."
        
        API_STATUS=$(curl -s -o /dev/null -w "%{http_code}" "http://127.0.0.1:8088/api/v1/diagnostic/health" 2>/dev/null)
        if [[ "$API_STATUS" == "200" ]]; then
            echo
            echo -e "${GREEN}✓ API server started successfully${NC}"
            break
        fi
        
        # If we've waited 10 seconds and still no response
        if [ $i -eq 10 ]; then
            echo
            echo -e "${RED}✗ API server failed to start properly${NC}"
            echo "Please check api_server_8088.log for details"
        fi
    done
fi

# Step 4: Check if frontend is already running
FRONTEND_RUNNING=false
if is_port_in_use 3001; then
    echo -e "${YELLOW}Port 3001 already in use, frontend may be running${NC}"
    FRONTEND_RUNNING=true
fi

# Step 5: Start frontend if not running
if [ "$FRONTEND_RUNNING" != "true" ]; then
    echo -e "${BLUE}Starting frontend development server...${NC}"
    
    cd "$(dirname "$0")/frontend"
    
    if [ -f "package.json" ]; then
        # Start frontend as background process
        nohup npm run dev > ../frontend_dev.log 2>&1 &
        FRONTEND_PID=$!
        
        echo "Started frontend with PID: $FRONTEND_PID"
        
        # Wait a bit for the frontend to start
        echo "Waiting for frontend to start..."
        sleep 5
    else
        echo -e "${RED}✗ Could not find frontend package.json${NC}"
        echo "Current directory: $(pwd)"
        echo "Please make sure you're running this script from the project root"
    fi
fi

# Step 6: Open the application in a browser
echo -e "${BLUE}Opening application in browser...${NC}"
sleep 2
xdg-open http://localhost:3001/ 2>/dev/null || open http://localhost:3001/ 2>/dev/null || start http://localhost:3001/ 2>/dev/null

echo
echo -e "${BOLD}===== Setup Complete =====${NC}"
echo -e "${GREEN}API server:${NC} http://localhost:8088/api/v1/diagnostic/health"
echo -e "${GREEN}Frontend:${NC} http://localhost:3001/"
echo -e "${GREEN}API Test Tool:${NC} http://localhost:3001/api-connection-test.html"
echo
echo -e "${BLUE}If you encounter any issues:${NC}"
echo "1. Check api_server_8088.log and frontend_dev.log for errors"
echo "2. Run the API Connection Test tool"
echo "3. See PORT_CONFIGURATION.md for more details"
