#!/bin/bash
# API Connection Fix Script
# This script fixes common issues with API connections for the AI Marketing Agent

# ANSI color codes
GREEN='\033[0;32m'
RED='\033[0;31m'
YELLOW='\033[0;33m'
BLUE='\033[0;34m'
NC='\033[0m' # No Color

echo -e "${BLUE}===== API Connection Fix =====${NC}"
echo "This script will attempt to fix API connection issues."

# Check if API server is running
echo -e "\n${YELLOW}Checking API Server Status:${NC}"
if curl --noproxy '*' -s -m 2 http://127.0.0.1:8088/api/v1/diagnostic/ping > /dev/null; then
    echo -e "${GREEN}✅ API server is running on port 8088${NC}"
else
    echo -e "${RED}❌ API server not running on port 8088${NC}"
    echo -e "Starting API server..."
    
    # Navigate to the project directory
    cd "$(dirname "$0")"
    
    # Try to activate the virtual environment
    if [ -d "venv" ]; then
        source venv/bin/activate
    else
        echo -e "${RED}❌ Virtual environment not found${NC}"
        echo -e "Creating a new virtual environment..."
        python3 -m venv venv
        source venv/bin/activate
        pip install -r requirements.txt
    fi
    
    # Start the API server in the background
    nohup python -m uvicorn app.main:app --host 0.0.0.0 --port 8088 > api_server.log 2>&1 &
    echo $! > api_server.pid
    echo -e "${GREEN}✅ API server started on port 8088${NC}"
    echo "Server logs are being saved to api_server.log"
    
    # Wait for server to start
    sleep 5
    
    # Verify the server started correctly
    if curl --noproxy '*' -s -m 2 http://127.0.0.1:8088/api/v1/diagnostic/ping > /dev/null; then
        echo -e "${GREEN}✅ API server is now running on port 8088${NC}"
    else
        echo -e "${RED}❌ API server failed to start${NC}"
        echo "Check api_server.log for more information"
        exit 1
    fi
fi

# Check if frontend server is running
echo -e "\n${YELLOW}Checking Frontend Server Status:${NC}"
if curl --noproxy '*' -s -m 2 http://127.0.0.1:3001 > /dev/null; then
    echo -e "${GREEN}✅ Frontend server is running on port 3001${NC}"
else
    echo -e "${RED}❌ Frontend server not running on port 3001${NC}"
    echo -e "Starting frontend server..."
    
    # Navigate to the frontend directory
    cd "$(dirname "$0")/frontend"
    
    # Start the frontend server in the background
    nohup npm run dev > ../frontend_server.log 2>&1 &
    echo $! > ../frontend_server.pid
    echo -e "${GREEN}✅ Frontend server started on port 3001${NC}"
    echo "Server logs are being saved to frontend_server.log"
    
    # Wait for server to start
    echo "Waiting for frontend server to start..."
    sleep 10
fi

# Clear browser cache instructions
echo -e "\n${YELLOW}Browser Cache:${NC}"
echo "To ensure proper functioning, clear your browser cache:"
echo " 1. Open Chrome Developer Tools (F12 or Ctrl+Shift+I)"
echo " 2. Right-click the refresh button and select 'Empty Cache and Hard Reload'"
echo " 3. Try accessing the application again"

# Verify proxy bypass settings
echo -e "\n${YELLOW}Verifying Proxy Bypass Settings:${NC}"
cd "$(dirname "$0")"

# Check if API_URL is set correctly in .env file
if [ -f "frontend/.env" ]; then
    echo "Checking frontend/.env file..."
    if grep -q "NEXT_PUBLIC_API_URL=http://127.0.0.1:8088/api/v1" frontend/.env; then
        echo -e "${GREEN}✅ NEXT_PUBLIC_API_URL is correctly set${NC}"
    else
        echo -e "${YELLOW}⚠️ Updating NEXT_PUBLIC_API_URL in .env file${NC}"
        echo "NEXT_PUBLIC_API_URL=http://127.0.0.1:8088/api/v1" > frontend/.env.tmp
        cat frontend/.env >> frontend/.env.tmp
        mv frontend/.env.tmp frontend/.env
        echo -e "${GREEN}✅ NEXT_PUBLIC_API_URL updated${NC}"
    fi
else
    echo -e "${YELLOW}⚠️ Creating .env file with correct settings${NC}"
    echo "NEXT_PUBLIC_API_URL=http://127.0.0.1:8088/api/v1" > frontend/.env
    echo -e "${GREEN}✅ Created .env file with API URL${NC}"
fi

# Test API connection with bypass proxy
echo -e "\n${YELLOW}Testing API Connection with Proxy Bypass:${NC}"
response=$(curl --noproxy '*' -s http://127.0.0.1:8088/api/v1/diagnostic/ping)
echo "Response: $response"

# Test authentication
echo -e "\n${YELLOW}Testing Authentication:${NC}"
auth_response=$(curl --noproxy '*' -s -X POST \
    -H "Content-Type: application/x-www-form-urlencoded" \
    -d "username=test@example.com&password=password" \
    http://127.0.0.1:8088/api/v1/auth/login)

if echo "$auth_response" | grep -q "access_token"; then
    echo -e "${GREEN}✅ Authentication successful${NC}"
    # Extract token
    token=$(echo "$auth_response" | grep -o '"access_token":"[^"]*' | cut -d'"' -f4)
    echo "Token received, length: ${#token} characters"
    
    # Save token for testing
    echo "$token" > auth_token.txt
    echo -e "${GREEN}✅ Token saved to auth_token.txt${NC}"
    
    echo -e "\n${YELLOW}Testing Protected Endpoint:${NC}"
    protected_response=$(curl --noproxy '*' -s -H "Authorization: Bearer $token" \
        http://127.0.0.1:8088/api/v1/diagnostic/health)
    echo "Response: $protected_response"
else
    echo -e "${RED}❌ Authentication failed${NC}"
    echo "Response: $auth_response"
fi

echo -e "\n${GREEN}===== API Connection Check Complete =====${NC}"
echo "If you continue to have issues:"
echo " 1. Check that both API and frontend servers are running"
echo " 2. Ensure you're using the test account: test@example.com / password"
echo " 3. Make sure no firewall or proxy is blocking local connections"
echo " 4. Try accessing the application at http://localhost:3001"
