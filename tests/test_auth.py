#!/usr/bin/env python3

import requests
import json
import sys

API_URL = "http://localhost:8088"
AUTH_TOKEN_FILE = "auth_token.json"

def get_auth_token():
    try:
        with open(AUTH_TOKEN_FILE, 'r') as f:
            data = json.load(f)
            return data.get("token")
    except Exception as e:
        print(f"Error reading auth token: {e}")
        return None

def test_auth():
    token = get_auth_token()
    if not token:
        print("❌ No auth token found")
        return False
    
    print(f"Using token: {token}")
    
    # Test with token
    try:
        headers = {"Authorization": f"Bearer {token}"}
        print(f"Testing API with headers: {headers}")
        
        # Try to access a protected endpoint
        response = requests.get(f"{API_URL}/api/companies/test_company", headers=headers)
        print(f"Response status: {response.status_code}")
        print(f"Response content: {response.text}")
        
        if response.status_code == 200:
            print("✅ Authentication successful")
            return True
        elif response.status_code == 403:
            print("❌ Authentication failed (403 Forbidden)")
            return False
        else:
            print(f"❌ Unexpected status code: {response.status_code}")
            return False
            
    except Exception as e:
        print(f"❌ Error testing auth: {e}")
        return False

if __name__ == "__main__":
    success = test_auth()
    sys.exit(0 if success else 1)
