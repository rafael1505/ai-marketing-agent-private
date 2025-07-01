#!/bin/bash

# Port Check Script for AI Marketing Agent
# This script validates that the required ports (8088 for API, 3001 for Frontend) are available

# Text formatting
BOLD='\033[1m'
GREEN='\033[0;32m'
YELLOW='\033[0;33m'
RED='\033[0;31m'
BLUE='\033[0;34m'
NC='\033[0m' # No Color

# Define the required ports
API_PORT=8088
FRONTEND_PORT=3001

echo -e "${BOLD}===== AI Marketing Agent Port Check =====${NC}"

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

# Function to find process using a port
find_process_on_port() {
    local port=$1
    local pid=""
    
    if command -v lsof &> /dev/null; then
        pid=$(lsof -t -i:$port 2>/dev/null)
    elif command -v netstat &> /dev/null; then
        if [[ "$OSTYPE" == "darwin"* ]]; then
            # macOS
            pid=$(netstat -anv | grep -E "\.${port}\s" | awk '{print $9}' | head -n1)
        else
            # Linux
            pid=$(netstat -tlnp 2>/dev/null | grep ":${port}" | awk '{print $7}' | cut -d'/' -f1 | head -n1)
        fi
    fi
    
    if [ -n "$pid" ]; then
        local cmd=""
        if [ -e "/proc/$pid/cmdline" ]; then
            cmd=$(tr '\0' ' ' < /proc/$pid/cmdline)
        elif command -v ps &> /dev/null; then
            cmd=$(ps -o command= -p $pid 2>/dev/null || ps -o args= -p $pid 2>/dev/null)
        fi
        
        echo "Process $pid: $cmd"
    else
        echo "Unknown process"
    fi
}

# Check API port
echo -e "${BLUE}Checking API port $API_PORT...${NC}"
if is_port_in_use $API_PORT; then
    # Check if it's our API
    API_STATUS=$(curl -s -o /dev/null -w "%{http_code}" "http://127.0.0.1:$API_PORT/api/v1/diagnostic/health" 2>/dev/null)
    if [[ "$API_STATUS" == "200" ]]; then
        echo -e "${GREEN}✓ API server is running correctly on port $API_PORT${NC}"
    else
        echo -e "${RED}✗ Port $API_PORT is in use by another service${NC}"
        find_process_on_port $API_PORT
        echo -e "${YELLOW}To free this port, run: python port_utils.py free-api${NC}"
    fi
else
    echo -e "${GREEN}✓ API port $API_PORT is available${NC}"
fi

# Check frontend port
echo -e "\n${BLUE}Checking frontend port $FRONTEND_PORT...${NC}"
if is_port_in_use $FRONTEND_PORT; then
    echo -e "${RED}✗ Port $FRONTEND_PORT is in use${NC}"
    find_process_on_port $FRONTEND_PORT
    echo -e "${YELLOW}To free this port, run: python port_utils.py free-frontend${NC}"
else
    echo -e "${GREEN}✓ Frontend port $FRONTEND_PORT is available${NC}"
fi

echo -e "\n${BOLD}For more details, see PORT_CONFIGURATION.md${NC}"
