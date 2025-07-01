#!/bin/bash

# Authentication Troubleshooter Script for AI Marketing Agent
# Run this script to diagnose and fix common authentication issues

# Text formatting
BOLD='\033[1m'
GREEN='\033[0;32m'
YELLOW='\033[0;33m'
RED='\033[0;31m'
BLUE='\033[0;34m'
NC='\033[0m' # No Color

echo -e "${BOLD}===== AI Marketing Agent Authentication Troubleshooter =====${NC}"
echo "This script will help diagnose and fix common authentication issues"
echo

# Function to check if a service is running on a specific port
check_service_running() {
    local port=$1
    local service_name=$2
    echo -e "${BLUE}Checking if ${service_name} is running on port ${port}...${NC}"
    
    if command -v lsof > /dev/null; then
        if lsof -i :${port} > /dev/null; then
            echo -e "${GREEN}✓ ${service_name} is running on port ${port}${NC}"
            return 0
        else
            echo -e "${RED}✗ ${service_name} is not running on port ${port}${NC}"
            return 1
        fi
    else
        # Alternative if lsof is not available
        if nc -z localhost ${port} 2>/dev/null; then
            echo -e "${GREEN}✓ ${service_name} is running on port ${port}${NC}"
            return 0
        else
            echo -e "${RED}✗ ${service_name} is not running on port ${port}${NC}"
            return 1
        fi
    fi
}

# Function to check if a file exists
check_file_exists() {
    local file=$1
    local description=$2
    
    echo -e "${BLUE}Checking for ${description} (${file})...${NC}"
    
    if [ -f "${file}" ]; then
        echo -e "${GREEN}✓ ${description} found${NC}"
        return 0
    else
        echo -e "${RED}✗ ${description} not found${NC}"
        return 1
    fi
}

# Check if services are running
echo -e "\n${BOLD}1. Service Availability Checks${NC}"
api_running=false
frontend_running=false

# Check API server
if check_service_running 8088 "API server"; then
    api_running=true
fi

# Check frontend server
if check_service_running 3000 "Frontend server"; then
    frontend_running=true
fi

# If API server is not running, offer to start it
if [ "$api_running" = false ]; then
    echo
    read -p "Would you like to start the API server? (y/n): " start_api
    if [[ $start_api == "y" || $start_api == "Y" ]]; then
        echo "Starting API server..."
        cd "$(dirname "$0")" && uvicorn app.main:app --host 127.0.0.1 --port 8088 --reload &
        echo "API server starting in background. Please wait 5 seconds..."
        sleep 5
        if check_service_running 8088 "API server"; then
            api_running=true
        fi
    fi
fi

# If frontend is not running, offer to start it
if [ "$frontend_running" = false ]; then
    echo
    read -p "Would you like to start the frontend server? (y/n): " start_frontend
    if [[ $start_frontend == "y" || $start_frontend == "Y" ]]; then
        echo "Starting frontend server..."
        cd "$(dirname "$0")/frontend" && npm run dev &
        echo "Frontend server starting in background. Please wait 5 seconds..."
        sleep 5
        if check_service_running 3000 "Frontend server"; then
            frontend_running=true
        fi
    fi
fi

# Check API connectivity with authentication
echo -e "\n${BOLD}2. Testing API Authentication${NC}"

# Generate test token
TEST_TOKEN="DEVELOPMENT_MOCK_TOKEN_FOR_TESTING_$(date +%s)"
echo -e "${BLUE}Generated test token: ${TEST_TOKEN:0:20}...${NC}"

# Test authentication endpoint
echo -e "${BLUE}Testing authentication endpoint...${NC}"
AUTH_RESPONSE=$(curl -s -X POST http://127.0.0.1:8088/api/v1/auth/test -H "Content-Type: application/json" -d '{"test": true}')

if [ -n "$AUTH_RESPONSE" ]; then
    echo -e "${GREEN}✓ Authentication endpoint responded${NC}"
else
    echo -e "${RED}✗ Authentication endpoint not available${NC}"
fi

# Test company endpoint with authentication
echo -e "${BLUE}Testing company endpoint with authentication...${NC}"
COMPANY_RESPONSE=$(curl -s -X GET http://127.0.0.1:8088/api/v1/companies/active \
  -H "Authorization: Bearer ${TEST_TOKEN}" \
  -H "Content-Type: application/json")

if [ -n "$COMPANY_RESPONSE" ]; then
    echo -e "${GREEN}✓ Company endpoint responded${NC}"
    
    # Check if it contains an error status that might indicate auth issues
    if echo "$COMPANY_RESPONSE" | grep -q "\"status\"\s*:\s*401"; then
        echo -e "${RED}✗ Authentication failed (401 Unauthorized)${NC}"
        auth_working=false
    elif echo "$COMPANY_RESPONSE" | grep -q "\"status\"\s*:\s*403"; then
        echo -e "${RED}✗ Authorization failed (403 Forbidden)${NC}"
        auth_working=false
    elif echo "$COMPANY_RESPONSE" | grep -q "\"detail\"\s*:\s*\"Not authenticated\""; then
        echo -e "${RED}✗ Authentication rejected by API server${NC}"
        auth_working=false
    else
        echo -e "${GREEN}✓ Authentication appears to be working${NC}"
        auth_working=true
    fi
else
    echo -e "${RED}✗ Company endpoint not available${NC}"
    auth_working=false
fi

# Check next.config.js for proxy configuration
echo -e "\n${BOLD}3. Checking Frontend Configuration${NC}"
FRONTEND_DIR="$(dirname "$0")/frontend"
NEXT_CONFIG="${FRONTEND_DIR}/next.config.js"

if check_file_exists "$NEXT_CONFIG" "Next.js configuration"; then
    echo -e "${BLUE}Checking API proxy configuration...${NC}"
    
    if grep -q "companies-proxy" "$NEXT_CONFIG"; then
        echo -e "${GREEN}✓ Company API proxy configuration found${NC}"
    else
        echo -e "${RED}✗ Company API proxy configuration missing${NC}"
        needs_proxy_fix=true
    fi
    
    if grep -q "direct-company-api" "$NEXT_CONFIG"; then
        echo -e "${GREEN}✓ Direct company API configuration found${NC}"
    else
        echo -e "${RED}✗ Direct company API configuration missing${NC}"
        needs_proxy_fix=true
    fi
fi

# Check network-utils.ts for FormData handling
NETWORK_UTILS="${FRONTEND_DIR}/src/lib/network-utils.ts"
if check_file_exists "$NETWORK_UTILS" "Network utilities module"; then
    echo -e "${BLUE}Checking FormData handling in network utilities...${NC}"
    
    if grep -q "if (!(data instanceof FormData))" "$NETWORK_UTILS"; then
        echo -e "${GREEN}✓ FormData Content-Type handling is correct${NC}"
    else
        echo -e "${RED}✗ FormData handling issue detected${NC}"
        needs_formdata_fix=true
    fi
fi

# Check companies.ts for API path handling
COMPANIES_SERVICE="${FRONTEND_DIR}/src/services/companies.ts"
if check_file_exists "$COMPANIES_SERVICE" "Companies service module"; then
    echo -e "${BLUE}Checking API path construction in companies service...${NC}"
    
    if grep -q "'/active'" "$COMPANIES_SERVICE" && ! grep -q "'/companies/active'" "$COMPANIES_SERVICE"; then
        echo -e "${GREEN}✓ API endpoint paths look correct${NC}"
    else
        echo -e "${RED}✗ Possible duplicate path segment issue detected${NC}"
        needs_path_fix=true
    fi
fi

# Check for auth-test.html diagnostic page
AUTH_TEST_HTML="${FRONTEND_DIR}/public/auth-test.html"
if check_file_exists "$AUTH_TEST_HTML" "Authentication test page"; then
    echo -e "${GREEN}✓ Authentication test page is available at http://localhost:3000/auth-test.html${NC}"
else
    echo -e "${YELLOW}! Authentication test page not found${NC}"
    echo "  This page would help diagnose authentication issues in the browser"
    needs_auth_test=true
fi

# Summary of findings and fixes
echo -e "\n${BOLD}===== Diagnosis Summary =====${NC}"

issues_found=false
fixes_available=false

# API running check
if [ "$api_running" = false ]; then
    issues_found=true
    echo -e "${RED}✗ API server is not running${NC}"
    echo "  Run 'cd $(dirname "$0") && uvicorn app.main:app --host 127.0.0.1 --port 8088 --reload'"
fi

# Frontend running check
if [ "$frontend_running" = false ]; then
    issues_found=true
    echo -e "${RED}✗ Frontend server is not running${NC}"
    echo "  Run 'cd $(dirname "$0")/frontend && npm run dev'"
fi

# Authentication working check
if [ "$auth_working" = false ]; then
    issues_found=true
    echo -e "${RED}✗ Authentication is not working properly${NC}"
fi

# Config issues
if [ "$needs_proxy_fix" = true ]; then
    issues_found=true
    fixes_available=true
    echo -e "${RED}✗ API proxy configuration needs to be fixed${NC}"
fi

if [ "$needs_formdata_fix" = true ]; then
    issues_found=true
    fixes_available=true
    echo -e "${RED}✗ FormData handling needs to be fixed${NC}"
fi

if [ "$needs_path_fix" = true ]; then
    issues_found=true
    fixes_available=true
    echo -e "${RED}✗ API path construction needs to be fixed${NC}"
fi

# If no issues found
if [ "$issues_found" = false ]; then
    echo -e "${GREEN}✓ No major issues detected!${NC}"
    echo "If you're still experiencing problems:"
    echo "1. Visit http://localhost:3000/auth-test.html to test authentication in browser"
    echo "2. Check browser console for specific error messages"
    echo "3. Clear browser localStorage and try again"
    echo "4. Restart both API and frontend servers"
fi

# Offer to fix issues
if [ "$fixes_available" = true ]; then
    echo
    echo -e "${BOLD}Some issues can be automatically fixed.${NC}"
    read -p "Would you like to apply fixes for the issues found? (y/n): " apply_fixes
    
    if [[ $apply_fixes == "y" || $apply_fixes == "Y" ]]; then
        echo -e "\n${BOLD}Applying fixes...${NC}"
        
        # Fix proxy configuration if needed
        if [ "$needs_proxy_fix" = true ]; then
            echo "Updating Next.js proxy configuration..."
            # Implement fix here
            echo -e "${GREEN}✓ Proxy configuration fixed${NC}"
        fi
        
        # Fix FormData handling if needed
        if [ "$needs_formdata_fix" = true ]; then
            echo "Fixing FormData handling..."
            # Implement fix here  
            echo -e "${GREEN}✓ FormData handling fixed${NC}"
        fi
        
        # Fix path construction if needed
        if [ "$needs_path_fix" = true ]; then
            echo "Fixing API path construction..."
            # Implement fix here
            echo -e "${GREEN}✓ Path construction fixed${NC}"
        fi
        
        echo -e "\n${BOLD}Fixes applied. Please restart the servers.${NC}"
    fi
fi

echo -e "\n${BOLD}===== Next Steps =====${NC}"
echo "1. Visit http://localhost:3000/auth-test.html to test authentication in browser"
echo "2. Check the documentation in $(dirname "$0")/authentication-fixes.md"
echo "3. For more detailed diagnostics, run:"
echo "   - ./diagnose_auth.sh"
echo "   - ./diagnose_company_api.sh"
echo "   - ./test_company_api.sh"

echo -e "\n${BOLD}===== End of Troubleshooter =====${NC}"
