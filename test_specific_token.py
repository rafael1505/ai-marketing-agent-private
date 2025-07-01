#!/usr/bin/env python3
"""
Test script for company information update with specific token format
This script verifies that the authentication fix allows company information to be saved
with the YourSignatureHere token format
"""
import requests
import json
import os
import sys
import time

# API Base URL
API_BASE_URL = "http://127.0.0.1:8088/api/v1"

# Create a test token with the format that's failing in the application
TEST_TOKEN = "eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9.eyJzdWIiOiJ0ZXN0QGV4YW1wbGUuY29tIiwibmFtZSI6IlRlc3QgVXNlciIsImlhdCI6MTY5NDYxMjMxMCwiZXhwIjo0ODQ4MzcyMzEwfQ.YourSignatureHere"

def test_company_update():
    """Test updating company information with specific JWT token format"""
    print("\n=== Testing Company Update with YourSignatureHere Token ===")
    
    # URL for company update
    company_id = "test_company"
    update_url = f"{API_BASE_URL}/companies/{company_id}"
    
    # Authorization header with Bearer token
    headers = {
        "Authorization": f"Bearer {TEST_TOKEN}"
        # Don't set Content-Type for multipart requests
    }
    
    # Create test data
    data = {
        "name": "Updated Company Name",
        "description": "This is an updated description from the test script",
        "brand_colors": json.dumps(["#FF5733", "#33FF57"])
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
            print("Company update successful!")
            print(f"Response: {json.dumps(response.json(), indent=2)}")
            return True
        else:
            print(f"Company update failed. Response: {response.text}")
            return False
    except Exception as e:
        print(f"Error during company update test: {e}")
        return False

def main():
    # Wait for API server to fully start
    print("Waiting for API server to be ready...")
    time.sleep(3)
    
    # Test company update with specific token
    success = test_company_update()
    return 0 if success else 1

if __name__ == "__main__":
    sys.exit(main())
