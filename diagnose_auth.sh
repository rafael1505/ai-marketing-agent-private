#!/bin/bash

# Authentication diagnostics script for AI Marketing Agent
# This script checks authentication between frontend and backend API

# Text formatting
BOLD='\033[1m'
GREEN='\033[0;32m'
YELLOW='\033[0;33m'
RED='\033[0;31m'
NC='\033[0m' # No Color

# Check if jq is installed
if ! command -v jq &> /dev/null; then
    echo -e "${YELLOW}Warning: jq is not installed. Some tests may not show formatted results.${NC}"
    JQ_AVAILABLE=false
else
    JQ_AVAILABLE=true
fi

echo -e "${BOLD}===== AI Marketing Agent Authentication Diagnostics =====${NC}"
echo "Running checks to identify authentication issues..."

# 1. Check if API server is running
echo -e "\n${BOLD}1. Checking API server status...${NC}"
if curl -s http://127.0.0.1:8088/api/v1/health > /dev/null; then
    echo -e "${GREEN}✓ API server is running${NC}"
else
    echo -e "${RED}✗ API server is not running or not reachable${NC}"
    echo "   Try starting the API server with: npm run api-dev"
    exit 1
fi

# 2. Check if frontend server is running
echo -e "\n${BOLD}2. Checking frontend server status...${NC}"
if curl -s http://localhost:3000 > /dev/null; then
    echo -e "${GREEN}✓ Frontend server is running${NC}"
else
    echo -e "${YELLOW}! Frontend server may not be running on port 3000${NC}"
    echo "   Try starting the frontend with: cd frontend && npm run dev"
fi

# 3. Test authentication endpoint
echo -e "\n${BOLD}3. Testing authentication endpoint...${NC}"
AUTH_RESPONSE=$(curl -s -X POST http://127.0.0.1:8088/api/v1/auth/test -H "Content-Type: application/json" -d '{"test": true}')

if [ -n "$AUTH_RESPONSE" ]; then
    echo -e "${GREEN}✓ Authentication endpoint responded${NC}"
    if [ "$JQ_AVAILABLE" = true ]; then
        echo "Response:"
        echo "$AUTH_RESPONSE" | jq
    else
        echo "Response: $AUTH_RESPONSE"
    fi
else
    echo -e "${RED}✗ Authentication endpoint test failed${NC}"
fi

# 4. Generate a test token and test company endpoint
echo -e "\n${BOLD}4. Testing company endpoint with test token...${NC}"
TEST_TOKEN="DEVELOPMENT_MOCK_TOKEN_FOR_TESTING"
COMPANY_RESPONSE=$(curl -s http://127.0.0.1:8088/api/v1/companies/test_company -H "Authorization: Bearer $TEST_TOKEN")

if [ -n "$COMPANY_RESPONSE" ]; then
    echo -e "${GREEN}✓ Company endpoint responded with test token${NC}"
    if [ "$JQ_AVAILABLE" = true ]; then
        echo "Response:"
        echo "$COMPANY_RESPONSE" | jq
    else
        echo "Response: $COMPANY_RESPONSE"
    fi
else
    echo -e "${RED}✗ Company endpoint test failed${NC}"
fi

# 5. Check proxy configuration
echo -e "\n${BOLD}5. Checking Next.js proxy configuration...${NC}"
if grep -q "companies-proxy" ./frontend/next.config.js; then
    echo -e "${GREEN}✓ Companies proxy configuration found in next.config.js${NC}"
else
    echo -e "${RED}✗ Companies proxy configuration not found in next.config.js${NC}"
fi

# 6. Test multipart/form-data authentication
echo -e "\n${BOLD}6. Testing multipart/form-data request with authentication...${NC}"
FORM_DATA_RESPONSE=$(curl -s -X POST http://127.0.0.1:8088/api/v1/auth/test-multipart \
  -H "Authorization: Bearer $TEST_TOKEN" \
  -F "test=true" \
  -F "name=test_file" \
  -F "file=@./diagnose_auth.sh")

if [ -n "$FORM_DATA_RESPONSE" ]; then
    echo -e "${GREEN}✓ Multipart/form-data test endpoint responded${NC}"
    if [ "$JQ_AVAILABLE" = true ]; then
        echo "Response:"
        echo "$FORM_DATA_RESPONSE" | jq 2>/dev/null || echo "$FORM_DATA_RESPONSE"
    else
        echo "Response: $FORM_DATA_RESPONSE"
    fi
else
    echo -e "${YELLOW}! Multipart/form-data test endpoint not available${NC}"
    echo "  This means we can't fully test multipart authentication"
fi

# Report summary
echo -e "\n${BOLD}===== Authentication Diagnosis Summary =====${NC}"
echo "Authentication system diagnosis completed."
echo -e "\n${BOLD}Recommendations:${NC}"
echo "1. Visit http://localhost:3000/auth-test.html to test authentication in the browser"
echo "2. Check that the token is stored correctly in localStorage"
echo "3. Verify that the FormData Content-Type header is not explicitly set in request"
echo "4. Confirm that the Authorization header is included in all API requests"

echo -e "\n${BOLD}If authentication issues persist:${NC}"
echo "1. Restart the API server (npm run api-dev)"
echo "2. Restart the frontend server (cd frontend && npm run dev)"
echo "3. Clear your browser cache and localStorage"
echo "4. Check browser developer console for CORS or network errors"

echo -e "\nScript completed."
