#!/bin/bash
#!/usr/bin/env bash

# Script to start the API server and run the comprehensive authentication test

echo -e "\n=== Starting Authentication Verification ===\n"

# First, stop any running API servers
echo "Stopping any running API servers..."
pkill -f "uvicorn app.main" || true

# Start the API server with a clean environment
echo "Starting API server..."
cd "$(dirname "$0")"
nohup uvicorn app.main:app --host 127.0.0.1 --port 8088 --reload > api_server.log 2>&1 &
API_PID=$!

# Give the API server time to start
echo "Waiting for API server to start..."
sleep 5

# Run the comprehensive authentication test
echo "Running comprehensive authentication test..."
python3 comprehensive_auth_test.py

# Capture the exit code
TEST_RESULT=$?

# Check if the test succeeded
if [ $TEST_RESULT -eq 0 ]; then
  echo -e "\n\033[0;32m✅ Authentication fixes were applied successfully!\033[0m"
  echo "The following issues have been fixed:"
  echo "1. FormData request authentication"
  echo "2. Multiple auth endpoints support (login/token)"
  echo "3. Proper token extraction from headers"
else
  echo -e "\n\033[0;31m❌ There may still be issues with the authentication system.\033[0m"
  echo "Please check the logs for more details."
fi

echo -e "\nVerification completed!"

# Optional: Stop the API server when done
# echo "Stopping API server..."
# kill $API_PID

exit $TEST_RESULT
