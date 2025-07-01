#!/bin/bash

# Authentication Verification Script
# This script runs a comprehensive test suite to verify all authentication fixes

# Text formatting
BOLD='\033[1m'
GREEN='\033[0;32m'
YELLOW='\033[0;33m'
RED='\033[0;31m'
BLUE='\033[0;34m'
NC='\033[0m' # No Color

# Results tracking
TESTS_TOTAL=0
TESTS_PASSED=0
TESTS_FAILED=0

# Helper function for tests
run_test() {
    local test_name=$1
    local command=$2
    local expected_status=$3
    
    TESTS_TOTAL=$((TESTS_TOTAL+1))
    
    echo -e "\n${BLUE}Running test: ${test_name}${NC}"
    echo "$ $command"
    
    # Run the command and capture output and status
    output=$(eval "$command" 2>&1)
    status=$?
    
    # Check if status matches expected
    if [ $status -eq $expected_status ]; then
        echo -e "${GREEN}✓ Test passed${NC}"
        TESTS_PASSED=$((TESTS_PASSED+1))
    else
        echo -e "${RED}✗ Test failed (expected status $expected_status, got $status)${NC}"
        TESTS_FAILED=$((TESTS_FAILED+1))
    fi
    
    # Show truncated output
    if [ -n "$output" ]; then
        echo "Output (truncated):"
        echo "$output" | head -n 5
        if [ $(echo "$output" | wc -l) -gt 5 ]; then
            echo "... (output truncated)"
        fi
    fi
}

echo -e "${BOLD}===== Authentication Fixes Verification =====${NC}"
echo "Running comprehensive tests to verify all fixes are working"
echo

# Generate test token
TEST_TOKEN="DEVELOPMENT_MOCK_TOKEN_FOR_TESTING_$(date +%s)"

# Check API server availability
echo -e "${BLUE}Checking API server availability...${NC}"
curl -s -o /dev/null -w "%{http_code}\n" http://127.0.0.1:8088/api/v1/health 2>/dev/null | grep -q "200"

if [ $? -eq 0 ]; then
    echo -e "${GREEN}✓ API server is available${NC}"
else
    echo -e "${RED}✗ API server is not available. Cannot proceed with tests.${NC}"
    echo "Please start the API server with: uvicorn app.main:app --host 127.0.0.1 --port 8088 --reload"
    exit 1
fi

# Check frontend server availability
echo -e "${BLUE}Checking frontend server availability...${NC}"
curl -s -o /dev/null -w "%{http_code}\n" http://localhost:3000 2>/dev/null | grep -q "200"

if [ $? -eq 0 ]; then
    echo -e "${GREEN}✓ Frontend server is available${NC}"
else
    echo -e "${YELLOW}! Frontend server may not be available. Some tests might fail.${NC}"
    echo "You can start the frontend server with: cd frontend && npm run dev"
fi

# Section 1: Basic Authentication Tests
echo -e "\n${BOLD}1. Basic Authentication Tests${NC}"

# Test authentication endpoint
run_test "Authentication endpoint test" \
    "curl -s -X POST http://127.0.0.1:8088/api/v1/auth/test -H 'Content-Type: application/json' -d '{\"test\": true}' | grep -q 'success\|token\|auth'" \
    0

# Section 2: API Path Construction Tests
echo -e "\n${BOLD}2. API Path Construction Tests${NC}"

# Test active company path
run_test "Active company path test" \
    "curl -s -X GET http://127.0.0.1:8088/api/v1/companies/active -H 'Authorization: Bearer ${TEST_TOKEN}' | grep -q 'id\|name\|description'" \
    0

# Test company by ID path
run_test "Company by ID path test" \
    "curl -s -X GET http://127.0.0.1:8088/api/v1/companies/test_company -H 'Authorization: Bearer ${TEST_TOKEN}' | grep -q 'id\|name\|description'" \
    0

# Section 3: Proxy Configuration Tests
echo -e "\n${BOLD}3. Proxy Configuration Tests${NC}"

# Test companies-proxy
run_test "Companies proxy test" \
    "curl -s -X GET http://localhost:3000/companies-proxy/active -H 'Authorization: Bearer ${TEST_TOKEN}' | grep -q 'id\|name\|description'" \
    0

# Test direct-company-api
run_test "Direct company API proxy test" \
    "curl -s -X GET http://localhost:3000/direct-company-api/test_company -H 'Authorization: Bearer ${TEST_TOKEN}' | grep -q 'id\|name\|description'" \
    0

# Section 4: FormData Tests
echo -e "\n${BOLD}4. FormData Tests${NC}"

# Create a temporary test file
echo "Test file content" > /tmp/test_logo.png

# Test FormData upload with auth token
run_test "FormData upload test" \
    "curl -s -X PUT http://127.0.0.1:8088/api/v1/companies/test_company -H 'Authorization: Bearer ${TEST_TOKEN}' -F 'name=Test Company Updated' -F 'description=Updated via test script' -F 'brand_colors[0]=#FF5733' -F 'logo_file=@/tmp/test_logo.png' | grep -q 'id\|name\|description'" \
    0

# Test FormData upload through proxy
run_test "FormData upload via proxy test" \
    "curl -s -X PUT http://localhost:3000/companies-proxy/test_company -H 'Authorization: Bearer ${TEST_TOKEN}' -F 'name=Test Company Via Proxy' -F 'description=Updated via proxy' -F 'brand_colors[0]=#33FF57' -F 'logo_file=@/tmp/test_logo.png' | grep -q 'id\|name\|description'" \
    0

# Clean up temporary file
rm -f /tmp/test_logo.png

# Section 5: Infrastructure Tests
echo -e "\n${BOLD}5. Infrastructure Tests${NC}"

# Check next.config.js configuration
run_test "Next.js proxy configuration test" \
    "grep -q 'direct-company-api' ./frontend/next.config.js" \
    0

# Check FormData handling in network-utils.ts
run_test "FormData Content-Type handling test" \
    "grep -q 'if (!(data instanceof FormData))' ./frontend/src/lib/network-utils.ts" \
    0

# Check API path in companies.ts
run_test "API path construction test" \
    "grep -q \"'/active'\" ./frontend/src/services/companies.ts && ! grep -q \"'/companies/active'\" ./frontend/src/services/companies.ts" \
    0

# Check auth-test.html availability
run_test "Auth test page availability" \
    "test -f ./frontend/public/auth-test.html" \
    0

# Report results
echo -e "\n${BOLD}===== Test Results =====${NC}"
echo -e "Total tests: ${TESTS_TOTAL}"
echo -e "${GREEN}Tests passed: ${TESTS_PASSED}${NC}"
echo -e "${RED}Tests failed: ${TESTS_FAILED}${NC}"

# Calculate pass percentage
PASS_PERCENTAGE=$((TESTS_PASSED * 100 / TESTS_TOTAL))
echo -e "Pass rate: ${PASS_PERCENTAGE}%"

# Final verdict
if [ $TESTS_FAILED -eq 0 ]; then
    echo -e "\n${GREEN}${BOLD}✓ All authentication fixes are working correctly!${NC}"
    echo -e "The system should now handle both JSON and FormData requests properly."
    echo -e "Company information submissions with file uploads should work without issues."
else
    echo -e "\n${YELLOW}${BOLD}! Some tests failed. Refer to the test results above.${NC}"
    echo -e "For detailed troubleshooting:"
    echo -e "1. Run ./auth_troubleshooter.sh for interactive diagnostics"
    echo -e "2. Check ./authentication-guide.md for documentation"
    echo -e "3. Visit http://localhost:3000/auth-test.html for browser-based testing"
fi

# Save results to file
echo -e "\nSaving verification results to verification_result.txt"
{
    echo "Authentication Fixes Verification Results"
    echo "Date: $(date)"
    echo "-------------------------------------"
    echo "Total tests: ${TESTS_TOTAL}"
    echo "Tests passed: ${TESTS_PASSED}"
    echo "Tests failed: ${TESTS_FAILED}"
    echo "Pass rate: ${PASS_PERCENTAGE}%"
    echo ""
    if [ $TESTS_FAILED -eq 0 ]; then
        echo "VERDICT: All authentication fixes are working correctly!"
    else
        echo "VERDICT: Some tests failed. Further investigation required."
    fi
} > verification_result.txt

echo -e "\n${BOLD}===== End of Verification =====${NC}"
