#!/bin/bash

# Final Verification Script for Authentication Fixes
# This script will verify all authentication fixes are working correctly

# Text formatting
BOLD='\033[1m'
GREEN='\033[0;32m'
YELLOW='\033[0;33m'
RED='\033[0;31m'
BLUE='\033[0;34m'
NC='\033[0m' # No Color

echo -e "${BOLD}===== Authentication Fixes Verification =====${NC}"
echo "This script will run a final verification of all authentication fixes."
echo

# Check API server availability
echo -e "${BLUE}Step 1: Checking API server availability...${NC}"
API_STATUS=$(curl -s -o /dev/null -w "%{http_code}" "http://127.0.0.1:8088/api/v1/diagnostic/health")

if [[ "$API_STATUS" == "200" ]]; then
    echo -e "${GREEN}✓ API server is running on port 8088${NC}"
else
    # Try port 8089 as a fallback
    API_STATUS=$(curl -s -o /dev/null -w "%{http_code}" "http://127.0.0.1:8089/api/v1/diagnostic/health")
    
    if [[ "$API_STATUS" == "200" ]]; then
        echo -e "${GREEN}✓ API server is running on port 8089${NC}"
        # Update the port for subsequent tests
        API_PORT=8089
    else
        echo -e "${RED}✗ API server is not running${NC}"
        echo "Please start the API server with:"
        echo "  uvicorn app.main:app --host 127.0.0.1 --port 8088 --reload"
        exit 1
    fi
fi

API_PORT=${API_PORT:-8089}
API_BASE="http://127.0.0.1:${API_PORT}/api/v1"

# Get authentication token
echo -e "\n${BLUE}Step 2: Setting up authentication token...${NC}"

# Try to get a real token first
TOKEN_RESPONSE=$(curl -s -X POST "${API_BASE}/auth/token" \
  -H "Content-Type: application/x-www-form-urlencoded" \
  -d "username=test@example.com&password=testpassword")

# Check if token retrieval succeeded
if echo "$TOKEN_RESPONSE" | grep -q "access_token"; then
    echo -e "${GREEN}✓ Successfully retrieved authentication token${NC}"
    # Extract token
    TOKEN=$(echo "$TOKEN_RESPONSE" | grep -o '"access_token":"[^"]*' | sed 's/"access_token":"//')
    echo "Token: ${TOKEN:0:15}..."
else
    # Use a development mock token as fallback
    echo -e "${YELLOW}! Using development mock token instead${NC}"
    TOKEN="DEVELOPMENT_MOCK_TOKEN_FOR_TESTING_$(date +%s)"
    echo "Token: ${TOKEN}"
fi

# Save token for other scripts to use
echo "{\"access_token\":\"$TOKEN\",\"token_type\":\"bearer\"}" > auth_token_fresh.json
echo "$TOKEN" > auth_token_new.txt

# Test JSON authentication
echo -e "\n${BLUE}Step 3: Testing JSON authentication...${NC}"
JSON_RESPONSE=$(curl -s -X POST "${API_BASE}/auth-test/test-json" \
  -H "Authorization: Bearer $TOKEN" \
  -H "Content-Type: application/json" \
  -d '{"test_key":"test_value"}')

if echo "$JSON_RESPONSE" | grep -q "success"; then
    echo -e "${GREEN}✓ JSON authentication working correctly${NC}"
else
    echo -e "${RED}✗ JSON authentication failed${NC}"
    echo "Response: $JSON_RESPONSE"
    echo "This suggests a problem with the standard authentication flow"
fi

# Test direct form endpoint (no auth dependency)
echo -e "\n${BLUE}Step 4: Testing direct FormData endpoint...${NC}"
DIRECT_FORM_RESPONSE=$(curl -s -X POST "${API_BASE}/auth-test/test-form-direct" \
  -H "Authorization: Bearer $TOKEN" \
  -F "test_field=test_value")

if echo "$DIRECT_FORM_RESPONSE" | grep -q "auth_header_present.*true"; then
    echo -e "${GREEN}✓ Direct FormData endpoint correctly received Authorization header${NC}"
else
    echo -e "${RED}✗ Direct FormData endpoint did not receive Authorization header${NC}"
    echo "Response: $DIRECT_FORM_RESPONSE"
    echo "This suggests the token is not being passed correctly in FormData requests"
fi

# Test FormData authentication with special dependency
echo -e "\n${BLUE}Step 5: Testing FormData authentication with special dependency...${NC}"
echo "This is test content" > test_logo.txt

FORM_RESPONSE=$(curl -s -X POST "${API_BASE}/auth-test/test-form-special" \
  -H "Authorization: Bearer $TOKEN" \
  -F "test_field=test_value" \
  -F "test_file=@test_logo.txt")

if echo "$FORM_RESPONSE" | grep -q "success"; then
    echo -e "${GREEN}✓ FormData authentication with special dependency working correctly${NC}"
else
    echo -e "${RED}✗ FormData authentication with special dependency failed${NC}"
    echo "Response: $FORM_RESPONSE"
    echo "This suggests a problem with the FormData-specific authentication dependency"
fi

# Test company update with FormData
echo -e "\n${BLUE}Step 6: Testing company update with FormData...${NC}"
COMPANY_RESPONSE=$(curl -s -X PUT "${API_BASE}/companies/test_company" \
  -H "Authorization: Bearer $TOKEN" \
  -F "name=Test Company Updated" \
  -F "description=Updated via verification script" \
  -F "email=test@updated.com" \
  -F "logo_file=@test_logo.txt")

if echo "$COMPANY_RESPONSE" | grep -q "name"; then
    echo -e "${GREEN}✓ Company update with FormData working correctly${NC}"
else
    echo -e "${RED}✗ Company update with FormData failed${NC}"
    echo "Response: $COMPANY_RESPONSE"
    echo "This suggests an issue with the company API endpoint"
fi

# Clean up
rm -f test_logo.txt

# Run comprehensive Python test
echo -e "\n${BLUE}Step 7: Running comprehensive Python tests...${NC}"
PYTHONPATH=. python test_auth_complete.py

# Final verdict
echo -e "\n${BOLD}===== Authentication Fixes Verification Complete =====${NC}"
echo "If all tests above passed, the authentication fixes are working correctly."
echo "If any test failed, please check the specific area that needs attention."
echo
echo "You can also view the comprehensive test results in the terminal output above."
echo -e "${BLUE}For further testing with a browser, visit:${NC}"
echo "  http://localhost:3000/auth-debug-suite.html"
