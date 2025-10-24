#!/usr/bin/env python3
"""
Simple script to verify authentication is working
"""
import requests
import json
import sys

# API Base URL
API_BASE_URL = "http://127.0.0.1:8088/api/v1"

def main():
    print("Testing API authentication...")
    
    # Step 1: Try to login
    print("\n=== Login Test ===")
    login_url = f"{API_BASE_URL}/auth/token"
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
            
            # Step 2: Test a protected endpoint
            print("\n=== Protected Endpoint Test ===")
            headers = {"Authorization": f"Bearer {token}"}
            
            health_url = f"{API_BASE_URL}/diagnostic/health"
            print(f"GET {health_url}")
            health_response = requests.get(health_url, headers=headers)
            print(f"Status: {health_response.status_code}")
            print(f"Response: {health_response.json()}")
            
            # Test companies endpoint
            companies_url = f"{API_BASE_URL}/companies/active"
            print(f"GET {companies_url}")
            companies_response = requests.get(companies_url, headers=headers)
            print(f"Status: {companies_response.status_code}")
            if companies_response.status_code == 200:
                print(f"Response: {json.dumps(companies_response.json(), indent=2)}")
            else:
                print(f"Error: {companies_response.text}")
        else:
            print(f"Login failed! Response: {response.text}")
            return 1
            
    except Exception as e:
        print(f"Error: {str(e)}")
        return 1
        
    return 0

if __name__ == "__main__":
    sys.exit(main())
