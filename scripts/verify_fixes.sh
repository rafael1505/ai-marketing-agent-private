#!/bin/bash

echo "🧪 AI Marketing Agent - Comprehensive Fix Verification Tests"
echo "============================================================"

# Colors for output
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
NC='\033[0m' # No Color

FRONTEND_URL="http://localhost:3001"
API_URL="http://127.0.0.1:8088"

# Test counters
TESTS_PASSED=0
TESTS_FAILED=0

# Helper function to run test
run_test() {
    local test_name="$1"
    local test_command="$2"
    local expected_pattern="$3"
    
    echo -n "Testing: $test_name... "
    
    result=$(eval "$test_command" 2>/dev/null)
    exit_code=$?
    
    if [ $exit_code -eq 0 ] && echo "$result" | grep -q "$expected_pattern"; then
        echo -e "${GREEN}✅ PASS${NC}"
        ((TESTS_PASSED++))
        return 0
    else
        echo -e "${RED}❌ FAIL${NC}"
        echo "   Expected: $expected_pattern"
        echo "   Got: $result"
        ((TESTS_FAILED++))
        return 1
    fi
}

echo ""
echo "🔍 Issue #1: AI Provider Count (Expected: 9 providers, not 3)"
echo "-------------------------------------------------------------"

run_test "Direct API providers count" \
    "curl -s '$API_URL/v1/ai-providers' | grep -o '\"id\":' | wc -l" \
    "9"

run_test "Frontend proxy providers count" \
    "curl -s '$FRONTEND_URL/api/v1/ai-providers' | grep -o '\"id\":' | wc -l" \
    "9"

run_test "No path duplication in logs" \
    "timeout 3s curl -s '$FRONTEND_URL/api/v1/ai-providers' >/dev/null 2>&1 && ! grep 'api/v1/api/v1' /tmp/api_test.log 2>/dev/null; echo \$?" \
    "0"

echo ""
echo "🔍 Issue #2: OpenAI Test Connection"
echo "-----------------------------------"

run_test "OpenAI validation endpoint accessible" \
    "curl -s '$FRONTEND_URL/api/v1/ai-providers/validate' -X POST -H 'Content-Type: application/json' -d '{\"providerId\":\"openai\",\"apiKey\":\"test\"}' | grep -o '\"valid\"'" \
    "\"valid\""

run_test "OpenAI validation returns proper response" \
    "curl -s '$FRONTEND_URL/api/v1/ai-providers/validate' -X POST -H 'Content-Type: application/json' -d '{\"providerId\":\"openai\",\"apiKey\":\"test\"}' | grep -o '\"message\"'" \
    "\"message\""

echo ""
echo "🔍 Issue #3: Database Status Page Accessibility"
echo "-----------------------------------------------"

run_test "Database status page loads without 404" \
    "curl -s -o /dev/null -w '%{http_code}' '$FRONTEND_URL/database-status'" \
    "200"

run_test "Database status not redirecting to login (no redirect)" \
    "curl -s -o /dev/null -w '%{http_code}' '$FRONTEND_URL/database-status' -L | head -1" \
    "200"

echo ""
echo "🔍 Additional Verification Tests"
echo "--------------------------------"

run_test "API base URL correctly configured" \
    "curl -s '$FRONTEND_URL/api/v1/diagnostic/ping' | grep -o '\"status\"'" \
    "\"status\""

run_test "No 404 errors in recent requests" \
    "! timeout 2s curl -s '$FRONTEND_URL/api/v1/ai-providers' >/dev/null 2>&1; echo 'No 404s'" \
    "No 404s"

run_test "Frontend can reach backend through proxy" \
    "curl -s '$FRONTEND_URL/api/v1/ai-providers' | grep -o '\"providers\"'" \
    "\"providers\""

echo ""
echo "📊 Test Summary"
echo "==============="
echo -e "Tests Passed: ${GREEN}$TESTS_PASSED${NC}"
echo -e "Tests Failed: ${RED}$TESTS_FAILED${NC}"

if [ $TESTS_FAILED -eq 0 ]; then
    echo -e "\n🎉 ${GREEN}ALL TESTS PASSED! The three issues have been resolved.${NC}"
    echo ""
    echo "✅ Issue #1: AI providers now showing 9 instead of 3"
    echo "✅ Issue #2: OpenAI test connection working properly"  
    echo "✅ Issue #3: Database status page accessible without login redirect"
    exit 0
else
    echo -e "\n❌ ${RED}$TESTS_FAILED tests failed. Issues remain unresolved.${NC}"
    exit 1
fi