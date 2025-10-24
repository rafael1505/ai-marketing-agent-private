#!/bin/bash

# Simple authentication test using curl with proper error handling
API_URL="http://127.0.0.1:8088/api/v1"

echo "Testing authentication endpoints..."

# Function to make a curl request and handle errors
function make_curl_request() {
  local url="$1"
  local method="$2"
  local headers=("${@:3:$#-3}")
  local data="${@: -1}"
  
  # Convert headers array to curl arguments
  local header_args=()
  for header in "${headers[@]}"; do
    header_args+=("-H" "$header")
  done
  
  # Make the request
  if [ "$method" == "GET" ]; then
    response=$(curl -s -X "$method" "${header_args[@]}" "$url")
  else
    response=$(curl -s -X "$method" "${header_args[@]}" -d "$data" "$url")
  fi
  
  # Check curl exit status
  if [ $? -ne 0 ]; then
    echo "Error: curl request failed"
    return 1
  fi
  
  # Check if response is valid JSON
  if echo "$response" | grep -q "^{"; then
    echo "$response"
    return 0
  else
    echo "Error: Invalid JSON response: $response"
    return 1
  fi
}

# Test login endpoint
echo "Testing login endpoint..."
login_response=$(make_curl_request "$API_URL/auth/login" "POST" "Content-Type: application/x-www-form-urlencoded" "username=test@example.com&password=testpassword")

if [[ $? -eq 0 && "$login_response" == *"access_token"* ]]; then
  echo "Login successful!"
  
  # Extract token
  token=$(echo "$login_response" | grep -o '"access_token":"[^"]*' | sed 's/"access_token":"//g')
  echo "Token: ${token:0:20}..."
  
  # Test protected endpoint
  echo "Testing protected endpoint..."
  companies_response=$(make_curl_request "$API_URL/companies/active" "GET" "Authorization: Bearer $token")
  
  if [[ $? -eq 0 && "$companies_response" == *"id"* ]]; then
    echo "Protected endpoint access successful!"
  else
    echo "Failed to access protected endpoint"
  fi
  
  # Test FormData endpoint
  echo "Testing FormData endpoint..."
  # Create a temporary file for testing
  echo "Test content" > test_file.txt
  
  formdata_response=$(curl -s -X POST "$API_URL/auth-test/test-form" \
    -H "Authorization: Bearer $token" \
    -F "test_field=TestValue" \
    -F "test_file=@test_file.txt")
  
  if [[ "$formdata_response" == *"status"* && "$formdata_response" == *"success"* ]]; then
    echo "FormData request successful!"
  else
    echo "Failed FormData request: $formdata_response"
  fi
  
  # Clean up
  rm -f test_file.txt
else
  echo "Login failed: $login_response"
fi
