#!/bin/bash

# API Port Reset Script
# This script checks if the API is running on the wrong port and restarts it
# on the correct port (8088)

# Text formatting
BOLD='\033[1m'
GREEN='\033[0;32m'
YELLOW='\033[0;33m'
RED='\033[0;31m'
BLUE='\033[0;34m'
NC='\033[0m' # No Color

echo -e "${BOLD}===== API Port Configuration Fix =====${NC}"
echo "This script will check and fix the API port configuration"
echo

# Check if API server is running on port 8088 (correct)
echo -e "${BLUE}Checking if API is running on correct port (8088)...${NC}"
API_STATUS_8088=$(curl -s -o /dev/null -w "%{http_code}" "http://127.0.0.1:8088/api/v1/diagnostic/health")

if [[ "$API_STATUS_8088" == "200" ]]; then
    echo -e "${GREEN}✓ API server is already running correctly on port 8088${NC}"
    echo "No action needed!"
else
    echo -e "${YELLOW}⚠️ API server not detected on port 8088${NC}"
    
    # Check if running on incorrect port 8089
    API_STATUS_8089=$(curl -s -o /dev/null -w "%{http_code}" "http://127.0.0.1:8089/api/v1/diagnostic/health")
    
    if [[ "$API_STATUS_8089" == "200" ]]; then
        echo -e "${RED}⚠️ ISSUE DETECTED: API server is running on the WRONG port (8089)!${NC}"
        
        # Find the process running on port 8089 and kill it
        echo -e "${BLUE}Stopping API server on incorrect port...${NC}"
        PID_8089=$(lsof -ti:8089)
        
        if [ ! -z "$PID_8089" ]; then
            echo -e "Killing process $PID_8089 running on port 8089"
            kill $PID_8089
            sleep 1
            
            # Double-check if it's killed
            if ps -p $PID_8089 > /dev/null; then
                echo -e "${RED}Process is still running, attempting to force kill...${NC}"
                kill -9 $PID_8089
                sleep 1
            fi
        fi
        
        echo -e "${GREEN}✓ API server on incorrect port has been stopped${NC}"
        
        # Start the API server on the correct port
        echo -e "${BLUE}Starting API server on correct port 8088...${NC}"
        cd "$(dirname "$0")" # Change to script directory
        nohup uvicorn app.main:app --host 127.0.0.1 --port 8088 --reload > api_server_8088.log 2>&1 &
        
        # Wait for it to start up
        echo "Waiting for API server to start..."
        sleep 3
        
        # Verify API server is now running on port 8088
        API_STATUS_8088=$(curl -s -o /dev/null -w "%{http_code}" "http://127.0.0.1:8088/api/v1/diagnostic/health")
        
        if [[ "$API_STATUS_8088" == "200" ]]; then
            echo -e "${GREEN}✓ SUCCESS: API server is now running correctly on port 8088${NC}"
        else
            echo -e "${RED}✗ ERROR: API server did not start correctly on port 8088${NC}"
            echo "Please check the log file: $(pwd)/api_server_8088.log"
        fi
    else
        echo -e "${YELLOW}API server doesn't appear to be running on either port${NC}"
        
        # Starting fresh on correct port
        echo -e "${BLUE}Starting API server on correct port 8088...${NC}"
        cd "$(dirname "$0")" # Change to script directory
        nohup uvicorn app.main:app --host 127.0.0.1 --port 8088 --reload > api_server_8088.log 2>&1 &
        
        # Wait for it to start up
        echo "Waiting for API server to start..."
        sleep 3
        
        # Verify API server is now running on port 8088
        API_STATUS_8088=$(curl -s -o /dev/null -w "%{http_code}" "http://127.0.0.1:8088/api/v1/diagnostic/health")
        
        if [[ "$API_STATUS_8088" == "200" ]]; then
            echo -e "${GREEN}✓ SUCCESS: API server is now running correctly on port 8088${NC}"
        else
            echo -e "${RED}✗ ERROR: API server did not start correctly on port 8088${NC}"
            echo "Please check the log file: $(pwd)/api_server_8088.log"
        fi
    fi
fi

echo
echo -e "${BOLD}===== Port Configuration Complete =====${NC}"
echo -e "For more information, see ${BOLD}PORT_CONFIGURATION.md${NC}"
