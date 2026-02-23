#!/bin/bash

# Development mock token
DEV_TOKEN="DEVELOPMENT_MOCK_TOKEN_FOR_TESTING"

# Colors
GREEN='\033[0;32m'
RED='\033[0;31m'
NC='\033[0m' # No Color

# Disable proxy for localhost
export no_proxy=localhost,127.0.0.1
unset http_proxy
unset https_proxy

echo -e "${GREEN}=== Testing Materials API ===${NC}"

# Test listing materials
echo -e "\n${GREEN}Testing list materials endpoint:${NC}"
curl -v -H "Authorization: Bearer $DEV_TOKEN" \
     -X GET \
     http://127.0.0.1:8088/api/v1/materials

# Create a test material
echo -e "\n${GREEN}Testing create material endpoint:${NC}"
MATERIAL_RESPONSE=$(curl -v -H "Authorization: Bearer $DEV_TOKEN" \
     -H "Content-Type: application/json" \
     -X POST \
     -d '{
        "title": "Test Marketing Material",
        "description": "A test material created via API",
        "target_audience": "Developers and testers",
        "campaign_objective": "Testing the material creation endpoint",
        "keywords": ["test", "api", "material"],
        "stage": "idea",
        "status": "draft"
     }' \
     http://127.0.0.1:8088/api/v1/materials)

echo "$MATERIAL_RESPONSE"

# Print a simplified version to get the material ID
# Can't parse JSON properly without jq, so just do a simple try
MATERIAL_RESPONSE_SIMPLE=$(echo "$MATERIAL_RESPONSE" | tr -d '\n')
if [[ $MATERIAL_RESPONSE_SIMPLE =~ \"id\":\"([^\"]+)\" ]]; then
    MATERIAL_ID="${BASH_REMATCH[1]}"
elif [[ $MATERIAL_RESPONSE_SIMPLE =~ \"_id\":\"([^\"]+)\" ]]; then
    MATERIAL_ID="${BASH_REMATCH[1]}"
else
    MATERIAL_ID=""
fi

if [ ! -z "$MATERIAL_ID" ]; then
    echo -e "\n${GREEN}Successfully created material with ID: $MATERIAL_ID${NC}"
    
    # Fetch the created material
    echo -e "\n${GREEN}Fetching created material:${NC}"
    curl -v -H "Authorization: Bearer $DEV_TOKEN" \
         -X GET \
         http://127.0.0.1:8088/api/v1/materials/$MATERIAL_ID
else
    echo -e "\n${RED}Failed to create material or get material ID${NC}"
fi

# List materials again to verify addition
echo -e "\n${GREEN}Listing materials again after creation:${NC}"
curl -v -H "Authorization: Bearer $DEV_TOKEN" \
     -X GET \
     http://127.0.0.1:8088/api/v1/materials
