#!/usr/bin/env python3
import requests
import json
import logging

# Setup logging
logging.basicConfig(level=logging.DEBUG, 
                   format='%(asctime)s - %(name)s - %(levelname)s - %(message)s')
logger = logging.getLogger(__name__)

# Test the login endpoint directly
print("Testing login endpoint directly...")
try:
    # Test with fixed test user
    response = requests.post(
        "http://127.0.0.1:8088/api/v1/auth/token",
        data={
            "username": "test@example.com",
            "password": "testpassword"
        },
        headers={"Content-Type": "application/x-www-form-urlencoded"},
        proxies={"http": None, "https": None}  # Bypass proxy
    )
    
    print(f"Status code: {response.status_code}")
    
    if response.status_code == 200:
        try:
            data = response.json()
            print(f"Response data: {json.dumps(data, indent=2)}")
            print(f"Token received: {data.get('access_token', '')[:20]}...")
            
            # Save token to a file for use in manual testing
            with open('auth_token_new.txt', 'w') as f:
                f.write(data.get('access_token', ''))
                print("Token saved to auth_token_new.txt")
        except json.JSONDecodeError:
            print(f"Failed to parse JSON response: {response.text}")
    else:
        print(f"Error response: {response.text}")
except Exception as e:
    print(f"Exception occurred: {str(e)}")

# Also test the proxy path
print("\nTesting auth-proxy endpoint...")
try:
    response = requests.post(
        "http://127.0.0.1:3001/auth-proxy/token",
        data={
            "username": "test@example.com",
            "password": "testpassword"
        },
        headers={"Content-Type": "application/x-www-form-urlencoded"},
        proxies={"http": None, "https": None}  # Bypass proxy
    )
    
    print(f"Status code: {response.status_code}")
    
    if response.status_code == 200:
        try:
            data = response.json()
            print(f"Response data: {json.dumps(data, indent=2)}")
            print(f"Token received: {data.get('access_token', '')[:20]}...")
        except json.JSONDecodeError:
            print(f"Failed to parse JSON response: {response.text}")
    else:
        print(f"Error response: {response.text}")
except Exception as e:
    print(f"Exception occurred: {str(e)}")
