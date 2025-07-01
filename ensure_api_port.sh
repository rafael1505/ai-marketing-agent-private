#!/bin/bash

# API Server Port Fix Script
# This script ensures the API server is running on the correct port (8088)

# Color codes for terminal output
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
NC='\033[0m' # No Color

echo -e "${YELLOW}=== API Server Port Fix ===${NC}"

# Check if port 8088 is already in use
echo -e "\nChecking port 8088..."
if netstat -tuln | grep -q ":8088 "; then
    echo -e "${YELLOW}Port 8088 is in use. Checking if it's our API server...${NC}"
    
    # Try to access the health endpoint
    if curl -s --head --fail "http://127.0.0.1:8088/api/v1/diagnostic/health" > /dev/null; then
        echo -e "${GREEN}✓ API server is already running on port 8088${NC}"
        echo "No action needed."
        exit 0
    else
        echo -e "${RED}✗ Something is using port 8088, but it's not our API server${NC}"
        echo "Will attempt to free the port..."
        
        # Try to kill the process using port 8088
        PID=$(lsof -ti:8088)
        if [ -n "$PID" ]; then
            echo "Killing process $PID using port 8088"
            kill -9 $PID
            sleep 1
            echo -e "${GREEN}Port 8088 has been freed${NC}"
        else
            echo -e "${RED}Failed to identify the process using port 8088${NC}"
            echo "Please manually check and kill any process using port 8088"
            exit 1
        fi
    fi
else
    echo -e "${GREEN}✓ Port 8088 is available${NC}"
fi

# Check if port 8089 (incorrect port) is in use by our API server
echo -e "\nChecking if API server is running on incorrect port 8089..."
if curl -s --head "http://127.0.0.1:8089/api/v1/diagnostic/health" > /dev/null 2>&1; then
    echo -e "${RED}✗ API server appears to be running on incorrect port 8089${NC}"
    
    # Try to kill the process
    PID=$(lsof -ti:8089)
    if [ -n "$PID" ]; then
        echo "Killing process $PID using port 8089"
        kill -9 $PID
        sleep 1
        echo -e "${GREEN}Process on port 8089 has been terminated${NC}"
    else
        echo -e "${RED}Failed to identify the process using port 8089${NC}"
    fi
else
    echo -e "${GREEN}✓ API server is not running on incorrect port 8089${NC}"
fi

# Start the API server on the correct port
echo -e "\nStarting API server on port 8088..."
cd "$(dirname "$0")"
python startup_server.py &

# Wait a bit for the server to start
sleep 3

# Verify the server is running on the correct port
if curl -s --head --fail "http://127.0.0.1:8088/api/v1/diagnostic/health" > /dev/null; then
    echo -e "${GREEN}✓ API server is now running correctly on port 8088${NC}"
    echo -e "${YELLOW}The API server is running in the background.${NC}"
    echo -e "${YELLOW}To stop it, find its process ID with 'ps aux | grep uvicorn' and use 'kill <PID>'${NC}"
    exit 0
else
    echo -e "${RED}✗ Failed to start API server on port 8088${NC}"
    echo "Please check the logs for errors"
    exit 1
fi
