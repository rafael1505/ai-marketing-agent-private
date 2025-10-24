#!/bin/bash

# Simplified authentication test script using curl
API_URL="http://127.0.0.1:8088/api/v1"
GREEN="\033[0;32m"
RED="\033[0;31m"
BLUE="\033[0;34m"
NC="\033[0m" # No Color

echo -e "\n${BLUE}=== Authentication Test Script ===${NC}\n"

# Function to check if a JSON response contains a specific key
contains_key() {
  local json="$1"
  local key="$2"
  echo "$json" | grep -q "\"$key\":"
  return $?
}

# Start the API server if it's not running
echo -e "${BLUE}Starting API server...${NC}"
if ! pgrep -f "uvicorn app.main" > /dev/null; then
  echo "API server not running. Starting it..."
  cd "$(dirname "$0")"
  nohup uvicorn app.main:app --host 127.0.0.1 --port 8088 > api_server.log 2>&1 &
  PID=$!
  echo "API server started with PID $PID"
  sleep 5 # Wait for server to start
else
  echo "API server is already running"
fi

# Check if API server is responding
echo -e "\n${BLUE}Testing API health...${NC}"
HEALTH_RESPONSE=$(curl -s "${API_URL}/diagnostic/health")
if [ $? -ne 0 ] || [ -z "$HEALTH_RESPONSE" ]; then
  echo -e "${RED}API server is not responding. Aborting tests.${NC}"
  cat api_server.log
  exit 1
fi
echo -e "${GREEN}API server is up and running.${NC}"
echo "Health response: $HEALTH_RESPONSE"

# Try to authenticate
echo -e "\n${BLUE}Testing authentication...${NC}"
echo "Testing /auth/login endpoint..."

# Create a temporary file for the form data
AUTH_DATA="username=test@example.com&password=testpassword"

# Try /auth/token endpoint first
echo "Trying /auth/token endpoint..."
LOGIN_RESPONSE=$(curl -s -X POST "${API_URL}/auth/token" \
  -H "Content-Type: application/x-www-form-urlencoded" \
  -d "$AUTH_DATA")

# Check if login succeeded
if contains_key "$LOGIN_RESPONSE" "access_token"; then
  TOKEN=$(echo "$LOGIN_RESPONSE" | grep -o '"access_token":"[^"]*' | sed 's/"access_token":"//g')
  echo -e "${GREEN}Login successful!${NC}"
  echo "Token: ${TOKEN:0:20}..."
else
  echo -e "${RED}Failed to authenticate with /auth/token.${NC}"
  echo "Trying /auth/login endpoint..."
  
  # Try /auth/login endpoint
  LOGIN_RESPONSE=$(curl -s -X POST "${API_URL}/auth/login" \
    -H "Content-Type: application/x-www-form-urlencoded" \
    -d "$AUTH_DATA")
    
  if contains_key "$LOGIN_RESPONSE" "access_token"; then
    TOKEN=$(echo "$LOGIN_RESPONSE" | grep -o '"access_token":"[^"]*' | sed 's/"access_token":"//g')
    echo -e "${GREEN}Login successful with /auth/login!${NC}"
    echo "Token: ${TOKEN:0:20}..."
  else
    echo -e "${RED}Authentication failed with both endpoints.${NC}"
    echo "Response: $LOGIN_RESPONSE"
    exit 1
  fi
fi

# Test JSON request with auth token
echo -e "\n${BLUE}Testing JSON request with auth token...${NC}"
JSON_RESPONSE=$(curl -s -X GET "${API_URL}/companies/active" \
  -H "Authorization: Bearer $TOKEN")

if [ $? -eq 0 ] && contains_key "$JSON_RESPONSE" "id"; then
  echo -e "${GREEN}JSON request successful!${NC}"
  echo "Response: ${JSON_RESPONSE:0:100}..."
else
  echo -e "${RED}JSON request failed.${NC}"
  echo "Response: $JSON_RESPONSE"
fi

# Test FormData request with auth token
echo -e "\n${BLUE}Testing FormData request...${NC}"
FORMDATA_RESPONSE=$(curl -s -X POST "${API_URL}/auth-test/test-form" \
  -H "Authorization: Bearer $TOKEN" \
  -F "test_field=TestValue" \
  -F "test_file=@auth_test.txt;filename=test.txt;type=text/plain")

if [ $? -eq 0 ] && contains_key "$FORMDATA_RESPONSE" "status"; then
  echo -e "${GREEN}FormData request successful!${NC}"
  echo "Response: ${FORMDATA_RESPONSE:0:100}..."
else
  echo -e "${RED}FormData request failed.${NC}"
  echo "Response: $FORMDATA_RESPONSE"
fi

# Test auth debug endpoint
echo -e "\n${BLUE}Testing auth debug endpoint...${NC}"
DEBUG_RESPONSE=$(curl -s -X GET "${API_URL}/auth-test/auth-debug" \
  -H "Authorization: Bearer $TOKEN")

if [ $? -eq 0 ] && contains_key "$DEBUG_RESPONSE" "has_auth_header"; then
  echo -e "${GREEN}Auth debug endpoint successful!${NC}"
  echo "Auth header detected: $(echo "$DEBUG_RESPONSE" | grep -o '"has_auth_header":[^,]*' | sed 's/"has_auth_header"://g')"
  echo "Token length: $(echo "$DEBUG_RESPONSE" | grep -o '"token_length":[^,]*' | sed 's/"token_length"://g')"
else
  echo -e "${RED}Auth debug endpoint failed.${NC}"
  echo "Response: $DEBUG_RESPONSE"
fi

echo -e "\n${BLUE}=== Authentication Test Complete ===${NC}\n"
