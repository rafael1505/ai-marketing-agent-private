#!/bin/bash

# Company API diagnostics script
# This script tests the company API endpoints specifically

# Text formatting
BOLD='\033[1m'
GREEN='\033[0;32m'
YELLOW='\033[0;33m'
RED='\033[0;31m'
NC='\033[0m' # No Color

echo -e "${BOLD}===== Company API Diagnostics =====${NC}"
echo "Testing company API endpoints..."

# Get the auth token
TOKEN=$(curl -s -X POST http://127.0.0.1:8088/api/v1/auth/login \
  -H "Content-Type: application/json" \
  -d '{"username": "test@example.com", "password": "password"}' | grep -o '"access_token":"[^"]*' | cut -d'"' -f4)

if [ -z "$TOKEN" ]; then
  echo -e "${RED}Failed to get authentication token. Cannot continue tests.${NC}"
  exit 1
else
  echo -e "${GREEN}✓ Got authentication token${NC}"
fi

echo -e "\n${BOLD}1. Testing GET active company endpoint...${NC}"
curl -s -X GET http://127.0.0.1:8088/api/v1/companies/active \
  -H "Authorization: Bearer $TOKEN" | jq

echo -e "\n${BOLD}2. Testing GET company by ID...${NC}"
curl -s -X GET http://127.0.0.1:8088/api/v1/companies/test_company \
  -H "Authorization: Bearer $TOKEN" | jq

# Create a temporary test file
echo "Test file content" > /tmp/test_logo.png

echo -e "\n${BOLD}3. Testing PUT company update with form data...${NC}"
curl -s -X PUT http://127.0.0.1:8088/api/v1/companies/test_company \
  -H "Authorization: Bearer $TOKEN" \
  -F "name=Test Company Updated" \
  -F "description=Updated Description" \
  -F "brand_colors[0]=#3B82F6" \
  -F "logo_file=@/tmp/test_logo.png" | jq

# Try alternate endpoint to verify
echo -e "\n${BOLD}4. Testing direct company path...${NC}"
curl -s -X GET http://127.0.0.1:8088/api/v1/companies/test_company \
  -H "Authorization: Bearer $TOKEN" | jq

# Clean up
rm /tmp/test_logo.png

echo -e "\n${BOLD}===== Company API Diagnostics Complete =====${NC}"
