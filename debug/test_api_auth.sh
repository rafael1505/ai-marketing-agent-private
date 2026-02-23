#!/bin/bash

# Test the API diagnostic endpoints
echo "Testing API diagnostic ping..."
no_proxy=127.0.0.1 http_proxy= https_proxy= curl -s http://127.0.0.1:8088/api/v1/diagnostic/ping | jq .

echo "Testing API database connection..."
no_proxy=127.0.0.1 http_proxy= https_proxy= curl -s http://127.0.0.1:8088/api/v1/diagnostic/debug-db | jq .

# Test authentication
echo "Testing authentication with test credentials..."
no_proxy=127.0.0.1 http_proxy= https_proxy= curl -v -X POST http://127.0.0.1:8088/api/v1/auth/login \
  -H "Content-Type: application/x-www-form-urlencoded" \
  -d "username=test@example.com&password=password"
