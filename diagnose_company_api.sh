#!/bin/bash

echo "===== API Connection Diagnosis ====="

# Check if the API server is running
echo "Checking if port 8088 is in use: `lsof -i :8088 >/dev/null && echo YES || echo NO`"
lsof -i :8088 | head -5

echo ""
echo "===== Testing API Connectivity ====="

# Test API direct connection
echo "Testing companies endpoint:"
curl -s -o /dev/null -w "%{http_code}\n" -H "Content-Type: application/json" http://127.0.0.1:8088/api/v1/companies/active || echo "Connection failed"

echo ""
echo "===== Testing with proxy bypass ====="
echo "Testing with NO_PROXY:"
NO_PROXY=127.0.0.1 HTTP_PROXY= HTTPS_PROXY= curl -v -s -o /dev/null -w "%{http_code}\n" http://127.0.0.1:8088/api/v1/companies/active 2>/dev/null || echo "Connection failed"

echo ""
echo "===== Frontend Configuration Check ====="
# Check the frontend API configuration
API_CONFIG=$(grep -r "API_URL" /mnt/c/Users/brc07274/OneDrive\ -\ Philips/Philips\ Files/BU\ -\ CI/Repository/AI\ Marketing\ Agent\ \(Python\)/ai-marketing-agent/frontend/src/ | head -1)
echo "Frontend API configuration: $API_CONFIG"

echo ""
echo "===== Network Interfaces ====="
# Show network interfaces
ip addr | grep -E "inet " | grep -v "127.0.0.1"

echo ""
echo "===== Recommendations ====="
echo "1. Clear browser cache and try again"
echo "2. Try accessing the test diagnostic page at: http://localhost:3001/api/diagnostic/company"
echo "3. Make sure the API server is running with: cd /path/to/project && uvicorn app.main:app --host 0.0.0.0 --port 8088 --reload"
echo "4. If behind corporate proxy, try running browser with proxy bypass for localhost"

echo ""
echo "===== End of Diagnosis ====="
