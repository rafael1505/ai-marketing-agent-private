#!/bin/bash

# API Server Port Fix Tool
# This script helps restart the API server on the correct port (8088)

# Text formatting
BOLD='\033[1m'
GREEN='\033[0;32m'
YELLOW='\033[0;33m'
RED='\033[0;31m'
BLUE='\033[0;34m'
NC='\033[0m' # No Color

echo -e "${BOLD}===== API Server Port Fix Tool =====${NC}"
echo "This tool will help restart the API server on the correct port"
echo

# Check current status
echo -e "${BLUE}Checking if API is running on the correct port (8088)...${NC}"
API_STATUS_8088=$(curl -s -o /dev/null -w "%{http_code}" "http://127.0.0.1:8088/api/v1/diagnostic/health" 2>/dev/null)

if [[ "$API_STATUS_8088" == "200" ]]; then
    echo -e "${GREEN}✓ SUCCESS: API server is already running correctly on port 8088${NC}"
    echo "No action needed."
    exit 0
fi

echo -e "${YELLOW}⚠️ API is not detected on port 8088${NC}"

# Check if running on wrong port
echo -e "${BLUE}Checking if API is running on incorrect port (8089)...${NC}"
API_STATUS_8089=$(curl -s -o /dev/null -w "%{http_code}" "http://127.0.0.1:8089/api/v1/diagnostic/health" 2>/dev/null)

if [[ "$API_STATUS_8089" == "200" ]]; then
    echo -e "${RED}⚠️ FOUND: API server is running on incorrect port 8089!${NC}"
    
    # Ask to kill the incorrect port
    read -p "Would you like to stop the API server on port 8089? (y/n) " -n 1 -r
    echo
    if [[ $REPLY =~ ^[Yy]$ ]]; then
        echo -e "${BLUE}Stopping API server on port 8089...${NC}"
        
        # Find and stop process using port 8089
        PID=$(lsof -t -i:8089 2>/dev/null)
        if [ -n "$PID" ]; then
            echo "Stopping process $PID using port 8089..."
            kill $PID
            sleep 2
            
            # Check if it was killed
            if kill -0 $PID 2>/dev/null; then
                echo -e "${YELLOW}Process still running, trying force kill...${NC}"
                kill -9 $PID
                sleep 1
            fi
            
            echo -e "${GREEN}Process stopped${NC}"
        else
            echo -e "${YELLOW}Could not find process using port 8089${NC}"
        fi
    fi
else
    echo -e "${YELLOW}No API server detected on port 8089 either${NC}"
fi

# Start API server on correct port
echo
read -p "Would you like to start the API server on port 8088? (y/n) " -n 1 -r
echo
if [[ $REPLY =~ ^[Yy]$ ]]; then
    echo -e "${BLUE}Starting API server on port 8088...${NC}"
    
    # Navigate to project root
    cd "$(dirname "$0")"
    
    # Current directory
    echo "Current directory: $(pwd)"
    
    # Check if running from project root
    if [ -f "app/main.py" ]; then
        echo "Found app/main.py, starting server..."
        nohup uvicorn app.main:app --host 127.0.0.1 --port 8088 --reload > api_server_8088.log 2>&1 &
        
        # Get the PID of the new process
        NEW_PID=$!
        echo "Started API server with PID: $NEW_PID"
        
        # Wait a moment for server to start
        echo "Waiting for API server to start..."
        sleep 5
        
        # Check if server started successfully
        NEW_API_STATUS=$(curl -s -o /dev/null -w "%{http_code}" "http://127.0.0.1:8088/api/v1/diagnostic/health" 2>/dev/null)
        if [[ "$NEW_API_STATUS" == "200" ]]; then
            echo -e "${GREEN}✓ SUCCESS: API server is now running correctly on port 8088${NC}"
            echo "You can now use the web application normally."
        else
            echo -e "${RED}✗ ERROR: Failed to start API server on port 8088${NC}"
            echo "Please check api_server_8088.log for details"
        fi
    else
        echo -e "${RED}✗ ERROR: Could not find app/main.py${NC}"
        echo "Make sure you're running this script from the project root"
        echo "Current files in directory:"
        ls -la | head -10
    fi
fi

echo
echo -e "${BOLD}===== Port Fix Complete =====${NC}"
echo "Remember to always start the API server with:"
echo -e "${GREEN}uvicorn app.main:app --host 127.0.0.1 --port 8088 --reload${NC}"
echo "For more information, see PORT_CONFIGURATION.md"
