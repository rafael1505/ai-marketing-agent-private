#!/usr/bin/env python3
"""
Test script for FormData uploads with authentication
"""
import requests
import json
import sys
import os

# API Base URL
API_BASE_URL = "http://127.0.0.1:8088/api/v1"

def main():
    print("Testing FormData uploads with authentication...")
    
        # Step 1: Try to login and get token
    print("\n=== Login Test ===")
    login_url = f"{API_BASE_URL}/auth/login"
    login_data = {
        "username": "test@example.com",
        "password": "testpassword"
    }
    
    try:
        print(f"POST {login_url}")
        response = requests.post(login_url, data=login_data)
        print(f"Status: {response.status_code}")
        
        if response.status_code == 200:
            print("Login successful!")
            token_data = response.json()
            token = token_data.get('access_token')
            print(f"Token: {token[:10]}...")
            
            # Step 2: Test FormData upload with auth
            print("\n=== FormData Upload Test ===")
            headers = {"Authorization": f"Bearer {token}"}
            
            # Create a test file
            test_file_path = "test_upload.txt"
            with open(test_file_path, "w") as f:
                f.write("This is a test file for FormData upload with authentication")
            
            # Test FormData with our new test endpoint
            test_url = f"{API_BASE_URL}/auth-test/test-form"
            print(f"POST {test_url} (FormData with file)")
            
            files = {
                "test_file": ("test_upload.txt", open(test_file_path, "rb"), "text/plain")
            }
            data = {
                "test_field": "Value from FormData test"
            }
            
            form_response = requests.post(
                test_url,
                headers=headers,  # Auth headers
                files=files,      # File part
                data=data         # Form fields
            )
            
            print(f"Status: {form_response.status_code}")
            if form_response.status_code == 200:
                print(f"Response: {json.dumps(form_response.json(), indent=2)}")
            else:
                print(f"Error: {form_response.text}")
            
            # Clean up the test file
            os.remove(test_file_path)
            
            # Step 3: Test company update with FormData
            print("\n=== Company Update Test (FormData) ===")
            
            company_url = f"{API_BASE_URL}/companies/test_company"
            print(f"PUT {company_url} (FormData with file)")
            
            # Create another test file for company logo
            logo_file_path = "test_logo.txt"
            with open(logo_file_path, "w") as f:
                f.write("This is a test logo file")
            
            company_files = {
                "logo_file": ("test_logo.txt", open(logo_file_path, "rb"), "text/plain")
            }
            
            company_data = {
                "name": "Updated Test Company via Python",
                "description": "This company was updated via Python FormData test",
                "brand_colors": json.dumps(["#FF0000", "#00FF00"]) 
            }
            
            company_response = requests.put(
                company_url,
                headers=headers,
                files=company_files,
                data=company_data
            )
            
            print(f"Status: {company_response.status_code}")
            if company_response.status_code == 200:
                print(f"Response: {json.dumps(company_response.json(), indent=2)}")
            else:
                print(f"Error: {company_response.text}")
            
            # Clean up the logo file
            os.remove(logo_file_path)
            
            return 0
        else:
            print(f"Login failed! Response: {response.text}")
            return 1
            
    except Exception as e:
        print(f"Error: {str(e)}")
        import traceback
        traceback.print_exc()
        return 1
        
if __name__ == "__main__":
    sys.exit(main())
