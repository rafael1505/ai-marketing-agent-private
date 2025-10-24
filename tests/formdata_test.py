#!/usr/bin/env python3
"""
Test script for FormData company update endpoint
"""

import requests
import json
import io
import time

# Configuration
API_BASE_URL = "http://127.0.0.1:8088"
LOGIN_URL = f"{API_BASE_URL}/api/v1/auth/token"
COMPANY_UPDATE_URL = f"{API_BASE_URL}/api/v1/companies/1"

def test_formdata_upload():
    print("=== FormData Upload Test ===")
    
    # Step 1: Login to get a fresh token
    print("1. Logging in to get fresh token...")
    login_data = {
        "username": "test@example.com",
        "password": "testpassword"
    }
    
    try:
        login_response = requests.post(LOGIN_URL, data=login_data, timeout=10)
        print(f"Login status: {login_response.status_code}")
        
        if login_response.status_code == 200:
            token_data = login_response.json()
            access_token = token_data.get("access_token")
            print(f"Token received: {access_token[:20]}...")
        else:
            print(f"Login failed: {login_response.text}")
            return
            
    except Exception as e:
        print(f"Login request failed: {e}")
        return
    
    # Step 2: Prepare FormData request
    print("2. Preparing FormData request...")
    
    headers = {
        "Authorization": f"Bearer {access_token}"
    }
    
    # Create a simple test file
    test_file_content = b"fake image content for testing"
    test_file = io.BytesIO(test_file_content)
    
    form_data = {
        "name": "Test Company Updated",
        "description": "Updated via FormData test",
        "email": "updated@test.com",
        "phone": "555-0123",
        "address": "123 Test St"
    }
    
    files = {
        "logo_file": ("test_logo.png", test_file, "image/png")
    }
    
    # Step 3: Make the FormData request with timeout
    print("3. Making FormData request...")
    print(f"URL: {COMPANY_UPDATE_URL}")
    print(f"Headers: {headers}")
    print(f"Form data: {form_data}")
    
    try:
        start_time = time.time()
        
        # Set a reasonable timeout to avoid hanging
        response = requests.put(
            COMPANY_UPDATE_URL, 
            headers=headers, 
            data=form_data, 
            files=files,
            timeout=30  # 30 second timeout
        )
        
        end_time = time.time()
        print(f"Request completed in {end_time - start_time:.2f} seconds")
        print(f"Response status: {response.status_code}")
        print(f"Response headers: {response.headers}")
        
        if response.status_code == 200:
            print("✓ FormData upload successful!")
            print(f"Response: {response.json()}")
        else:
            print(f"✗ FormData upload failed: {response.status_code}")
            print(f"Response: {response.text}")
            
    except requests.exceptions.Timeout:
        print("✗ Request timed out after 30 seconds - this indicates a hanging issue")
    except requests.exceptions.ConnectionError as e:
        print(f"✗ Connection error: {e}")
    except Exception as e:
        print(f"✗ Unexpected error: {e}")

if __name__ == "__main__":
    test_formdata_upload()
