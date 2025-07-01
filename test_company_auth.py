#!/usr/bin/env python3
"""
Test script for company information update with authentication
This script verifies that the authentication fix allows company information to be saved
"""
import requests
import json
import os
import sys

# API Base URL
API_BASE_URL = "http://127.0.0.1:8088/api/v1"

# Get the token from auth_token_fresh.json
def get_token():
    try:
        with open("auth_token_fresh.json", "r") as f:
            token_data = json.load(f)
            return token_data.get("access_token")
    except Exception as e:
        print(f"Error loading token: {e}")
        return None

def test_company_update():
    """Test updating company information with JWT token authentication"""
    print("\n=== Testing Company Update with Authentication ===")
    
    # Get the auth token
    token = get_token()
    if not token:
        print("No token available. Please make sure auth_token_fresh.json exists.")
        return False
    
    # URL for company update
    company_id = "test_company"
    update_url = f"{API_BASE_URL}/companies/{company_id}"
    
    # Authorization header with Bearer token
    headers = {
        "Authorization": f"Bearer {token}"
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

if __name__ == "__main__":
    success = test_company_update()
    sys.exit(0 if success else 1)
