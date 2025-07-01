#!/usr/bin/env python3
import requests
import sys
import json
import os

# Disable proxy for local connections
os.environ['NO_PROXY'] = 'localhost,127.0.0.1'

# Token received from the authentication endpoint
TOKEN = "eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9.eyJzdWIiOiIxIiwiZXhwIjoxNzQ5MjI2NTA3fQ.FjCS8TFDtLx-4lOVixUwxxFtOb25qIu3NdecAftXJus"

API_BASE_URL = "http://127.0.0.1:8088/api/v1"

def test_protected_endpoint():
    """Test access to a protected endpoint using the token"""
    headers = {"Authorization": f"Bearer {TOKEN}"}
    
    # Try multiple protected endpoints
    endpoints = [
        "/users/me", 
        "/companies/active",
        "/diagnostic/health"
    ]
    
    print("\n=== Testing Protected Endpoints ===")
    
    for endpoint in endpoints:
        url = f"{API_BASE_URL}{endpoint}"
        print(f"\nTesting endpoint: {url}")
        
        try:
            # Make the request with the auth token
            response = requests.get(url, headers=headers)
            
            # Print the results
            print(f"Status: {response.status_code}")
            if response.status_code == 200:
                print("✅ Success! Authentication is working correctly.")
                print("Response data:")
                print(json.dumps(response.json(), indent=2)[:400])  # Print first 400 chars
            else:
                print("❌ Failed to access protected endpoint")
                print(f"Error: {response.text}")
        except Exception as e:
            print(f"❌ Error during request: {e}")

if __name__ == "__main__":
    test_protected_endpoint()
