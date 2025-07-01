#!/usr/bin/env python3
"""
Direct auth test for API endpoints
"""

import requests
import json
import sys
import traceback

# API Base URL - update if needed
API_BASE_URL = "http://127.0.0.1:8088"

def test_login():
    """Test login API to get authentication token"""
    print("==== Testing Login API ====")
    login_url = f"{API_BASE_URL}/api/v1/auth/token"
    
    # Test credentials - these should match a user in the mock database
    login_data = {
        "username": "test@example.com",  # Use test user from mock data
        "password": "testpassword"       # Default test password
    }
    
    try:
        # Make login request
        print(f"Making POST request to: {login_url}")
        print(f"With data: {login_data}")
        
        response = requests.post(login_url, data=login_data)
        
        # Print response details
        print(f"Status code: {response.status_code}")
        print(f"Response headers: {response.headers}")
        
        if response.status_code == 200:
            data = response.json()
            print(f"Login successful! Got token: {data.get('access_token')[:15]}...")
            token = data.get('access_token')
            return token
        else:
            print(f"Login failed. Response: {response.text}")
            return None
    except Exception as e:
        print(f"Error during login test: {e}")
        traceback.print_exc()
        return None

def test_auth_header_formats(token):
    """Test different authentication header formats"""
    print("\n==== Testing Auth Header Formats ====")
    
    if not token:
        print("No token available. Skipping auth header tests.")
        return
    
    # Endpoint to test against
    test_url = f"{API_BASE_URL}/api/v1/companies/active"
    
    # Test different header formats
    auth_headers = [
        {"Authorization": f"Bearer {token}"},
        {"Authorization": f"bearer {token}"},
        {"authorization": f"Bearer {token}"},
        {"Authorization": token},
    ]
    
    for i, headers in enumerate(auth_headers):
        print(f"\nTest {i+1}: Header format: {headers}")
        try:
            response = requests.get(test_url, headers=headers)
            print(f"Status code: {response.status_code}")
            
            if response.status_code == 200:
                print("Request successful!")
                return headers  # Return the successful header format
            else:
                print(f"Request failed: {response.text}")
        except Exception as e:
            print(f"Error during request: {e}")
    
    print("All header formats failed.")
    return None

def test_company_upload(token):
    """Test PUT request with FormData for company update"""
    print("\n==== Testing Company Update with FormData ====")
    
    if not token:
        print("No token available. Skipping company upload test.")
        return
    
    # URL for company update
    company_id = "test_company"
    update_url = f"{API_BASE_URL}/api/v1/companies/{company_id}"
    
    # Authorization header 
    headers = {
        "Authorization": f"Bearer {token}"
        # Note: Don't set Content-Type for multipart requests
    }
    
    # Create test data
    data = {
        "name": "Updated Test Company",
        "description": "This is a test from the auth test script",
        "brand_colors": json.dumps(["#FF5733", "#33FF57"])  # JSON-encoded list
    }
    
    # Create a simple file for testing
    files = {
        "logo_file": ("test_logo.txt", b"This is test file content", "text/plain")
    }
    
    try:
        print(f"Making PUT request to: {update_url}")
        print(f"With data: {data}")
        print(f"With file: {files['logo_file'][0]}")
        print(f"Using headers: {headers}")
        
        # Make the request
        response = requests.put(update_url, headers=headers, data=data, files=files)
        
        # Print response details
        print(f"Status code: {response.status_code}")
        print(f"Response headers: {dict(response.headers)}")
        
        if response.status_code == 200:
            print("Company update successful!")
            return True
        else:
            print(f"Company update failed. Response: {response.text}")
            return False
    except Exception as e:
        print(f"Error during company update test: {e}")
        traceback.print_exc()
        return False

def main():
    try:
        # Step 1: Test login
        token = test_login()
        if not token:
            print("Login failed. Cannot continue tests.")
            sys.exit(1)
        
        # Step 2: Test auth header formats
        working_header = test_auth_header_formats(token)
        
        # Step 3: Test company upload with FormData
        upload_success = test_company_upload(token)
        
        # Print summary
        print("\n==== Test Summary ====")
        print(f"Login test: {'PASSED' if token else 'FAILED'}")
        print(f"Auth header test: {'PASSED' if working_header else 'FAILED'}")
        print(f"Company upload test: {'PASSED' if upload_success else 'FAILED'}")
        
        if not upload_success:
            sys.exit(1)
            
    except Exception as e:
        print(f"Error in main: {e}")
        traceback.print_exc()
        sys.exit(1)

if __name__ == "__main__":
    main()
