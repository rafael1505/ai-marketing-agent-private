#!/bin/bash
#!/usr/bin/env bash

# Authentication Fixes Verification Script
# This script tests all the authentication fixes to ensure they work properly

echo -e "\n=== Authentication Fixes Verification Script ===\n"

# Set API base URL
API_BASE="http://127.0.0.1:8088/api/v1"
GREEN='\033[0;32m'
RED='\033[0;31m'
BLUE='\033[0;34m'
NC='\033[0m' # No Color

# Function to display test status
test_status() {
  if [ $1 -eq 0 ]; then
    echo -e "${GREEN}✅ PASS${NC}: $2"
  else
    echo -e "${RED}❌ FAIL${NC}: $2"
    FAILURES=$((FAILURES+1))
  fi
}

# Function to check if servers are running
check_servers() {
  echo -e "${BLUE}Checking if API server is running...${NC}"
  curl -s "$API_BASE/diagnostic/health" > /dev/null
  if [ $? -ne 0 ]; then
    echo -e "${RED}ERROR: API server is not running. Please start it first.${NC}"
    echo "Run: uvicorn app.main:app --host 127.0.0.1 --port 8088"
    exit 1
  fi
  echo -e "${GREEN}API server is running.${NC}"
  
  echo -e "${BLUE}Checking if frontend server is running...${NC}"
  curl -s "http://localhost:3000" > /dev/null
  if [ $? -ne 0 ]; then
    echo -e "${YELLOW}WARNING: Frontend server may not be running. Some tests might fail.${NC}"
    echo "Run: cd frontend && npm run dev"
  else
    echo -e "${GREEN}Frontend server is running.${NC}"
  fi
}

# Initialize counter for failed tests
FAILURES=0

# Step 1: Check if the servers are running
check_servers

# Step 2: Get an authentication token
echo -e "\n${BLUE}Getting authentication token...${NC}"
echo "Trying to login with test@example.com / testpassword"
LOGIN_RESPONSE=$(curl -v -X POST "$API_BASE/auth/token" \
  -d "username=test@example.com&password=testpassword" 2>&1)

echo "Login response:"
echo "$LOGIN_RESPONSE"

# Check if login succeeded
TOKEN=$(echo "$LOGIN_RESPONSE" | grep -o '"access_token":"[^"]*' | sed 's/"access_token":"//')
if [ -z "$TOKEN" ]; then
  echo -e "${RED}Failed to get authentication token. Response shown above.${NC}"
  exit 1
fi

echo -e "${GREEN}Successfully obtained auth token.${NC}"
TOKEN_PREVIEW="${TOKEN:0:15}..."
echo "Token: $TOKEN_PREVIEW"

# Step 3: Test basic auth with JSON request
echo -e "\n${BLUE}Testing basic authentication with JSON...${NC}"
JSON_AUTH_RESPONSE=$(curl -s -X GET "$API_BASE/companies/active" \
  -H "Authorization: Bearer $TOKEN")

echo $JSON_AUTH_RESPONSE | grep -q "id"
test_status $? "Basic authentication with JSON request"

# Step 4: Test auth-debug endpoint
echo -e "\n${BLUE}Testing auth-debug endpoint...${NC}"
AUTH_DEBUG_RESPONSE=$(curl -s -X GET "$API_BASE/auth-test/auth-debug" \
  -H "Authorization: Bearer $TOKEN")

echo $AUTH_DEBUG_RESPONSE | grep -q "has_auth_header"
test_status $? "Auth-debug endpoint"

# Step 5: Test FormData with file upload (using a temp file)
echo -e "\n${BLUE}Testing FormData with file upload...${NC}"
echo "This is test content" > test_logo.txt

# Create a boundary for the multipart request
BOUNDARY="----WebKitFormBoundary7MA4YWxkTrZu0gW"

# Create the multipart request body
FORM_DATA=$(cat << EOF
--$BOUNDARY
Content-Disposition: form-data; name="test_field"

TestValue
--$BOUNDARY
Content-Disposition: form-data; name="test_file"; filename="test_logo.txt"
Content-Type: text/plain

$(cat test_logo.txt)
--$BOUNDARY--
EOF
)

# Make the request with the correct content type including boundary
FORM_AUTH_RESPONSE=$(curl -s -X POST "$API_BASE/auth-test/test-form" \
  -H "Authorization: Bearer $TOKEN" \
  -H "Content-Type: multipart/form-data; boundary=$BOUNDARY" \
  --data-binary "$FORM_DATA")

echo $FORM_AUTH_RESPONSE | grep -q '"status":"success"'
test_status $? "FormData with file upload"

# Clean up the test file
rm -f test_logo.txt

# Step 6: Test company update with FormData
echo -e "\n${BLUE}Testing company update with FormData...${NC}"
echo "Test logo content" > company_logo.txt

# Create the multipart request body for company update
COMPANY_FORM_DATA=$(cat << EOF
--$BOUNDARY
Content-Disposition: form-data; name="name"

Updated Test Company
--$BOUNDARY
Content-Disposition: form-data; name="description"

This is a test description from the verification script
--$BOUNDARY
Content-Disposition: form-data; name="brand_colors"

["#FF5733", "#33FF57"]
--$BOUNDARY
Content-Disposition: form-data; name="logo_file"; filename="company_logo.txt"
Content-Type: text/plain

$(cat company_logo.txt)
--$BOUNDARY--
EOF
)

# Make the company update request
COMPANY_UPDATE_RESPONSE=$(curl -s -X PUT "$API_BASE/companies/test_company" \
  -H "Authorization: Bearer $TOKEN" \
  -H "Content-Type: multipart/form-data; boundary=$BOUNDARY" \
  --data-binary "$COMPANY_FORM_DATA")

echo $COMPANY_UPDATE_RESPONSE | grep -q '"id":"test_company"'
test_status $? "Company update with FormData"

# Clean up the test company logo file
rm -f company_logo.txt

# Final report
echo -e "\n${BLUE}=== Test Summary ===${NC}"
if [ $FAILURES -eq 0 ]; then
  echo -e "${GREEN}All authentication tests passed successfully! 🎉${NC}"
else
  echo -e "${RED}$FAILURES test(s) failed. Check the output above for details.${NC}"
fi

echo -e "\nTo test the web interface, open the Authentication Debug Suite:"
echo -e "${BLUE}http://localhost:3000/auth-debug-suite.html${NC}"
echo ""
echo "Done!"

exit $FAILURES
