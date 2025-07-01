#!/bin/bash
# API Connection Checker Script
# Tests connections to the API server on ports 8088 and 8089

# ANSI color codes
GREEN='\033[0;32m'
RED='\033[0;31m'
YELLOW='\033[0;33m'
BLUE='\033[0;34m'
NC='\033[0m' # No Color

echo -e "${BLUE}===== API Connection Checker =====${NC}"
echo "Testing connections to API server..."

# Test port 8088
echo -e "\n${YELLOW}Testing port 8088 (Correct port):${NC}"
if curl --noproxy '*' -s -m 2 http://127.0.0.1:8088/api/v1/diagnostic/ping > /dev/null; then
    echo -e "${GREEN}✅ API server is running on port 8088${NC}"
    
    # Get more detailed information
    response=$(curl --noproxy '*' -s http://127.0.0.1:8088/api/v1/diagnostic/ping)
    echo "Response: $response"
    
    # Test authentication on port 8088
    echo -e "\n${YELLOW}Testing authentication on port 8088:${NC}"
    auth_response=$(curl --noproxy '*' -s -X POST \
        -H "Content-Type: application/x-www-form-urlencoded" \
        -d "username=test@example.com&password=password" \
        http://127.0.0.1:8088/api/v1/auth/login)
    
    if echo "$auth_response" | grep -q "access_token"; then
        echo -e "${GREEN}✅ Authentication successful${NC}"
        echo "Response: $auth_response"
        
        # Extract token for further tests
        token=$(echo "$auth_response" | grep -o '"access_token":"[^"]*' | cut -d'"' -f4)
        
        # Test protected endpoint
        echo -e "\n${YELLOW}Testing protected endpoint with token:${NC}"
        protected_response=$(curl --noproxy '*' -s -H "Authorization: Bearer $token" \
            http://127.0.0.1:8088/api/v1/diagnostic/health)
        echo "Response: $protected_response"
    else
        echo -e "${RED}❌ Authentication failed${NC}"
        echo "Response: $auth_response"
    fi
else
    echo -e "${RED}❌ API server not running on port 8088${NC}"
fi

# Test port 8089 (incorrect port)
echo -e "\n${YELLOW}Testing port 8089 (Incorrect port):${NC}"
if curl --noproxy '*' -s -m 2 http://127.0.0.1:8089/api/v1/diagnostic/ping > /dev/null; then
    echo -e "${RED}❌ API server is running on incorrect port 8089${NC}"
    echo "This may cause connectivity issues with the frontend."
    echo "You should use port 8088 instead."
else
    echo -e "${GREEN}✅ API is not running on port 8089 (correct)${NC}"
fi

# Test frontend connection to API
echo -e "\n${YELLOW}Testing frontend connection:${NC}"
echo "Frontend should be configured to use port 8088 for API connections."
echo "Browser based connectivity can be tested using the API Connection Test page."

# Summary
echo -e "\n${BLUE}===== Connection Summary =====${NC}"
if curl --noproxy '*' -s -m 2 http://127.0.0.1:8088/api/v1/diagnostic/ping > /dev/null; then
    echo -e "${GREEN}✅ API is available on the correct port (8088)${NC}"
    echo "The frontend should be configured to connect to http://localhost:8088"
    echo "or http://127.0.0.1:8088 for API requests."
else
    echo -e "${RED}❌ API connection issue detected${NC}"
    echo "Please ensure the API server is running on port 8088."
    echo "Run the following task to start the API server:"
    echo "  VS Code Task: 'Run API (Mock Database)'"
fi

echo -e "\n${BLUE}===== End of Connection Test =====${NC}"