#!/bin/bash

# Marketing Agent Master Startup Script
# This script provides a complete solution for starting the application with correct port configuration

# Text formatting
BOLD='\033[1m'
GREEN='\033[0;32m'
YELLOW='\033[0;33m'
RED='\033[0;31m'
BLUE='\033[0;34m'
NC='\033[0m' # No Color

echo -e "${BOLD}===== AI Marketing Agent Complete Startup =====${NC}"
echo "This script will ensure everything is configured correctly and running properly."
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

# Step 1: Generate authentication token for development
echo -e "${BLUE}Step 1: Generating authentication token...${NC}"
python generate_auth_token.py

# Step 2: Check and free required ports if necessary
echo -e "${BLUE}Step 2: Checking required ports...${NC}"
./check_ports.sh

# If API port is in use by something that's not our API
if is_port_in_use 8088; then
    echo -e "${YELLOW}⚠️ Port 8088 is already in use${NC}"
    # Check if it's our API
    API_STATUS=$(curl -s -o /dev/null -w "%{http_code}" "http://127.0.0.1:8088/api/v1/diagnostic/health" 2>/dev/null)
    if [[ "$API_STATUS" == "200" ]]; then
        echo -e "${GREEN}✓ API server is already running correctly on port 8088${NC}"
        API_RUNNING=true
    else
        echo -e "${RED}✗ Port 8088 is in use by another application${NC}"
        echo "Trying to free port 8088..."
        python port_utils.py free-api
    fi
else
    API_RUNNING=false
fi

# Check if frontend port is in use
if is_port_in_use 3001; then
    echo -e "${YELLOW}⚠️ Port 3001 is already in use${NC}"
    # Try to determine if it's our frontend
    FRONTEND_CHECK=$(curl -s -I "http://127.0.0.1:3001" | grep -i "next.js" || echo "")
    if [[ -n "$FRONTEND_CHECK" ]]; then
        echo -e "${GREEN}✓ Frontend is already running on port 3001${NC}"
        FRONTEND_RUNNING=true
    else
        echo -e "${RED}✗ Port 3001 is in use by another application${NC}"
        echo "Trying to free port 3001..."
        python port_utils.py free-frontend
    fi
else
    FRONTEND_RUNNING=false
fi

# Step 3: Start API server if not running
if [ "$API_RUNNING" != "true" ]; then
    echo -e "${BLUE}Step 3: Starting API server on port 8088...${NC}"
    
    echo "Checking Python environment and dependencies..."
    if pip list | grep -q uvicorn; then
        echo -e "${GREEN}✓ Uvicorn is installed${NC}"
    else
        echo -e "${YELLOW}Installing Uvicorn...${NC}"
        pip install uvicorn
    fi
    
    cd "$(dirname "$0")"
    
    # Start API server as background process
    echo "Starting API server..."
    nohup uvicorn app.main:app --host 127.0.0.1 --port 8088 --reload > api_server_8088.log 2>&1 &
    API_PID=$!
    
    echo "Started API server with PID: $API_PID"
    
    # Wait for API server to start
    echo -n "Waiting for API server to start..."
    for i in {1..15}; do
        sleep 1
        echo -n "."
        
        API_STATUS=$(curl -s -o /dev/null -w "%{http_code}" "http://127.0.0.1:8088/api/v1/diagnostic/health" 2>/dev/null)
        if [[ "$API_STATUS" == "200" ]]; then
            echo
            echo -e "${GREEN}✓ API server started successfully${NC}"
            break
        fi
        
        # If we've waited 15 seconds and still no response
        if [ $i -eq 15 ]; then
            echo
            echo -e "${RED}✗ API server failed to start properly${NC}"
            echo "Please check api_server_8088.log for details"
        fi
    done
fi

# Step 4: Start frontend if not running
if [ "$FRONTEND_RUNNING" != "true" ]; then
    echo -e "${BLUE}Step 4: Starting frontend server on port 3001...${NC}"
    
    cd "$(dirname "$0")/frontend"
    
    if [ -f "package.json" ]; then
        # Check if node_modules exists
        if [ ! -d "node_modules" ]; then
            echo "Installing frontend dependencies (this may take a few minutes)..."
            npm install
        fi
        
        # Start frontend as background process
        echo "Starting frontend server..."
        nohup npm run dev > ../frontend_dev.log 2>&1 &
        FRONTEND_PID=$!
        
        echo "Started frontend with PID: $FRONTEND_PID"
        
        # Wait a bit for the frontend to start
        echo -n "Waiting for frontend to start..."
        for i in {1..15}; do
            sleep 1
            echo -n "."
        done
        echo
        echo -e "${GREEN}✓ Frontend should now be starting${NC}"
    else
        echo -e "${RED}✗ Could not find frontend package.json${NC}"
        echo "Current directory: $(pwd)"
        echo "Please make sure you're running this script from the project root"
    fi
    
    # Return to project root
    cd "$(dirname "$0")"
fi

# Step 5: Open authentication helper page
echo -e "${BLUE}Step 5: Opening authentication helper page...${NC}"
sleep 2
xdg-open http://localhost:3001/auth-helper.html 2>/dev/null || open http://localhost:3001/auth-helper.html 2>/dev/null || start http://localhost:3001/auth-helper.html 2>/dev/null

# Step 6: Open the application in a browser
echo -e "${BLUE}Step 6: Opening main application...${NC}"
sleep 2
xdg-open http://localhost:3001/settings 2>/dev/null || open http://localhost:3001/settings 2>/dev/null || start http://localhost:3001/settings 2>/dev/null

echo
echo -e "${BOLD}===== Setup Complete =====${NC}"
echo -e "${GREEN}API Server:${NC} http://localhost:8088/api/v1/diagnostic/health"
echo -e "${GREEN}Frontend:${NC} http://localhost:3001/"
echo -e "${GREEN}Authentication Helper:${NC} http://localhost:3001/auth-helper.html" 
echo -e "${GREEN}Settings Page:${NC} http://localhost:3001/settings"
echo
echo -e "${BLUE}If you encounter any issues:${NC}"
echo "1. Check api_server_8088.log and frontend_dev.log for errors"
echo "2. Run the Authentication Helper to ensure your auth token is valid"
echo "3. See PORT_CONFIGURATION.md and authentication-guide.md for more details"
