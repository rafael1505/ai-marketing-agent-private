#!/usr/bin/env python3
"""
Test script to directly test company API endpoints with authenticated requests.
This bypasses the frontend and tests the backend API directly.
"""

import requests
import json
import sys
import traceback
from pprint import pprint

# API Base URL
API_BASE_URL = "http://127.0.0.1:8088"

def login_and_get_token():
    """Log in and obtain authentication token"""
    print("Attempting to login and get token...")
    login_url = f"{API_BASE_URL}/api/v1/auth/token"
    
    # Using the test user credentials 
    login_data = {
        "username": "test@example.com",
        "password": "testpassword"  # Default password for test user
    }
    
    response = requests.post(login_url, data=login_data)
    
    if response.status_code == 200:
        token_data = response.json()
        print(f"Login successful! Token type: {token_data.get('token_type')}")
        print(f"Token preview: {token_data.get('access_token')[:15]}...")
        return token_data.get('access_token')
    else:
        print(f"Login failed with status {response.status_code}")
        print(f"Response: {response.text}")
        return None

def test_get_company(token, company_id="test_company"):
    """Test GET request for company"""
    print(f"\nTesting GET company: {company_id}")
    
    headers = {
        "Authorization": f"Bearer {token}"
    }
    
    # Try both API path patterns
    urls = [
        f"{API_BASE_URL}/api/v1/companies/{company_id}",
        f"{API_BASE_URL}/api/v1/{company_id}"  # Alternative path that's causing 404s
    ]
    
    for url in urls:
        print(f"Testing URL: {url}")
        response = requests.get(url, headers=headers)
        
        print(f"Status code: {response.status_code}")
        if response.status_code == 200:
            data = response.json()
            print("Success! Company data:")
            pprint(data)
        else:
            print(f"Failed: {response.text}")
        print("-" * 40)

def test_update_company(token, company_id="test_company"):
    """Test PUT request to update company with regular JSON data"""
    print(f"\nTesting PUT company (regular JSON): {company_id}")
    
    headers = {
        "Authorization": f"Bearer {token}",
        "Content-Type": "application/json"
    }
    
    # Simple company data without file
    company_data = {
        "name": "Updated Test Company",
        "description": "This is an updated test company via direct API",
        "brand_colors": ["#3B82F6", "#93C5FD"]
    }
    
    # Try both API path patterns
    urls = [
        f"{API_BASE_URL}/api/v1/companies/{company_id}",
        f"{API_BASE_URL}/api/v1/{company_id}"  # Alternative path that's causing 404s
    ]
    
    for url in urls:
        print(f"Testing URL: {url}")
        response = requests.put(url, headers=headers, json=company_data)
        
        print(f"Status code: {response.status_code}")
        if response.status_code == 200:
            data = response.json()
            print("Success! Updated company data:")
            pprint(data)
        else:
            print(f"Failed: {response.text}")
        print("-" * 40)

def test_multipart_update(token, company_id="test_company"):
    """Test PUT request with multipart form data (simulating file upload)"""
    print(f"\nTesting PUT company with multipart form data: {company_id}")
    
    headers = {
        "Authorization": f"Bearer {token}"
        # Note: Don't set Content-Type header for multipart requests
    }
    
    # Company data as form fields
    company_data = {
        "name": "Multipart Test Company",
        "description": "This is a test company updated with multipart form",
        "brand_colors": json.dumps(["#3B82F6", "#93C5FD"])
    }
    
    # Create a dummy file
    files = {
        "logo_file": ("test_logo.png", open("test_direct_company_api.py", "rb"), "image/png")
    }
    
    # Try both API path patterns
    urls = [
        f"{API_BASE_URL}/api/v1/companies/{company_id}",
        f"{API_BASE_URL}/api/v1/{company_id}"  # Alternative path that's causing 404s
    ]
    
    for url in urls:
        print(f"Testing URL: {url}")
        response = requests.put(url, headers=headers, data=company_data, files=files)
        
        print(f"Status code: {response.status_code}")
        if response.status_code == 200:
            data = response.json()
            print("Success! Updated company data:")
            pprint(data)
        else:
            print(f"Failed: {response.text}")
        print("-" * 40)

def debug_auth_verification(token):
    """Check token and debug authentication verification"""
    print("\nDebugging token and auth verification:")
    print(f"Token type: {type(token)}")
    print(f"Token length: {len(token)}")
    print(f"Token preview: {token[:15]}...")
    
    # Make a simple authenticated request to the API
    debug_url = f"{API_BASE_URL}/api/v1/auth/verify"
    headers = {"Authorization": f"Bearer {token}"}
    
    print("\nVerifying token with auth endpoint...")
    try:
        response = requests.get(debug_url, headers=headers)
        print(f"Status code: {response.status_code}")
        print(f"Response: {response.text}")
    except Exception as e:
        print(f"Error during verification: {str(e)}")

def main():
    try:
        # Get token via login
        token = login_and_get_token()
        if not token:
            print("Failed to obtain token. Exiting.")
            sys.exit(1)
        
        # Debug auth verification
        debug_auth_verification(token)
        
        # Test GET company endpoint
        test_get_company(token)
        
        # Test PUT with JSON data
        test_update_company(token)
        
        # Test PUT with multipart form data (simulating file upload)
        test_multipart_update(token)
    except Exception as e:
        print(f"Error in main function: {str(e)}")
        print("Traceback:")
        traceback.print_exc()
        sys.exit(1)

if __name__ == "__main__":
    main()
