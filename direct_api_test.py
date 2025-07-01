#!/usr/bin/env python3
"""
Direct API testing script for the AI Marketing Agent
This script tests various endpoints to verify functionality
"""
import requests
import json
import sys
import time

# API Base URL
API_BASE_URL = "http://127.0.0.1:8088/api/v1"

# Fixed test token that matches the frontend format
TEST_TOKEN = "eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9.eyJzdWIiOiJ0ZXN0QGV4YW1wbGUuY29tIiwibmFtZSI6IlRlc3QgVXNlciIsImlhdCI6MTY5NDYxMjMxMCwiZXhwIjo0ODQ4MzcyMzEwfQ.YourSignatureHere"

def check_api_server():
    """Check if the API server is running and responding"""
    try:
        response = requests.get(f"{API_BASE_URL}/diagnostic/ping", timeout=2)
        if response.status_code == 200:
            print(f"✅ API server is running - {response.text}")
            return True
        else:
            print(f"❌ API server returned unexpected status: {response.status_code}")
            return False
    except Exception as e:
        print(f"❌ API server check failed: {e}")
        return False

def test_auth_token():
    """Test the authentication token with a simple endpoint"""
    print("\n=== Testing Authentication Token ===")
    
    headers = {"Authorization": f"Bearer {TEST_TOKEN}"}
    url = f"{API_BASE_URL}/users/me"
    
    try:
        response = requests.get(url, headers=headers)
        print(f"Status code: {response.status_code}")
        
        if response.status_code == 200:
            print("✅ Authentication successful!")
            print(f"Response: {json.dumps(response.json(), indent=2)}")
            return True
        else:
            print(f"❌ Authentication failed. Response: {response.text}")
            return False
    except Exception as e:
        print(f"❌ Error during authentication test: {e}")
        return False

def test_company_update():
    """Test updating company information with FormData"""
    print("\n=== Testing Company Update with FormData ===")
    
    # URL for company update
    company_id = "test_company"
    update_url = f"{API_BASE_URL}/companies/{company_id}"
    
    # Authorization header
    headers = {"Authorization": f"Bearer {TEST_TOKEN}"}
    
    # Create test data
    data = {
        "name": f"Updated Test Company - {time.strftime('%H:%M:%S')}",
        "description": "This is an updated description from the direct API test",
        "email": "test@example.com", 
        "phone": "555-TEST",
        "brand_colors": json.dumps(["#FF5733", "#33FF57"])  # JSON-encoded list
    }
    
    # Create a simple test file
    file_content = b"This is test file content for company logo"
    files = {
        "logo_file": ("test_logo.txt", file_content, "text/plain")
    }
    
    try:
        print(f"Making PUT request to: {update_url}")
        print(f"With headers: {headers}")
        print(f"With data: {data}")
        
        # Make the request with form data and file
        response = requests.put(update_url, headers=headers, data=data, files=files)
        
        # Print response details
        print(f"Status code: {response.status_code}")
        
        if response.status_code == 200:
            print("✅ Company update successful!")
            print(f"Response: {json.dumps(response.json(), indent=2)}")
            return True
        else:
            print(f"❌ Company update failed. Response: {response.text}")
            return False
    except Exception as e:
        print(f"❌ Error during company update test: {e}")
        return False

def main():
    # Wait for API server to fully start
    print("Checking if API server is ready...")
    if not check_api_server():
        print("API server is not responding. Exiting.")
        return 1
    
    # Test authentication
    auth_success = test_auth_token()
    
    # Test company update
    if auth_success:
        company_success = test_company_update()
    else:
        company_success = False
    
    # Print summary
    print("\n=== Test Summary ===")
    print(f"Authentication test: {'PASSED' if auth_success else 'FAILED'}")
    print(f"Company update test: {'PASSED' if company_success else 'FAILED'}")
    
    # Return success if all tests pass
    return 0 if (auth_success and company_success) else 1

if __name__ == "__main__":
    sys.exit(main())
