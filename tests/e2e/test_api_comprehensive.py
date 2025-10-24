#!/usr/bin/env python3
"""
Comprehensive API test to verify the server is working correctly
"""
import requests
import os
import json
import sys

# Disable proxy for localhost connections
os.environ['NO_PROXY'] = 'localhost,127.0.0.1'

API_BASE = "http://127.0.0.1:8088/api/v1"

def test_login():
    print("\n===== Testing login endpoint =====")
    login_url = f"{API_BASE}/auth/login"
    login_data = {
        "username": "test@example.com",
        "password": "password"
    }
    
    try:
        print(f"POST {login_url}")
        response = requests.post(login_url, data=login_data)
        print(f"Status: {response.status_code}")
        
        if response.status_code == 200:
            data = response.json()
            token = data.get('access_token')
            print(f"Login successful! Token: {token[:20]}...")
            return token
        else:
            print(f"Login failed! Response: {response.text}")
            return None
    except Exception as e:
        print(f"Error during login: {e}")
        return None

def test_protected_endpoint(token):
    print("\n===== Testing protected endpoint =====")
    if not token:
        print("Cannot test protected endpoint without token")
        return False
    
    me_url = f"{API_BASE}/users/me"
    headers = {"Authorization": f"Bearer {token}"}
    
    try:
        print(f"GET {me_url}")
        response = requests.get(me_url, headers=headers)
        print(f"Status: {response.status_code}")
        
        if response.status_code == 200:
            data = response.json()
            print(f"Success! User data: {json.dumps(data, indent=2)}")
            return True
        else:
            print(f"Failed to get user data! Response: {response.text}")
            return False
    except Exception as e:
        print(f"Error testing protected endpoint: {e}")
        return False

def test_diagnostic():
    print("\n===== Testing diagnostic endpoints =====")
    
    endpoints = [
        "/diagnostic/ping",
        "/diagnostic/health",
        "/diagnostic/debug-db"
    ]
    
    all_passed = True
    
    for endpoint in endpoints:
        url = f"{API_BASE}{endpoint}"
        try:
            print(f"\nGET {url}")
            response = requests.get(url)
            print(f"Status: {response.status_code}")
            
            if response.status_code == 200:
                data = response.json()
                print(f"Success! Response: {json.dumps(data, indent=2)}")
            else:
                print(f"Failed! Response: {response.text}")
                all_passed = False
        except Exception as e:
            print(f"Error testing {endpoint}: {e}")
            all_passed = False
    
    return all_passed

def main():
    # Test diagnostic endpoints
    if not test_diagnostic():
        print("\n❌ Diagnostic tests failed")
    else:
        print("\n✅ Diagnostic tests passed")
    
    # Test authentication
    token = test_login()
    if not token:
        print("\n❌ Authentication test failed")
        return 1
    
    if not test_protected_endpoint(token):
        print("\n❌ Protected endpoint test failed")
        return 1
    else:
        print("\n✅ All tests passed!")
        return 0

if __name__ == "__main__":
    sys.exit(main())
