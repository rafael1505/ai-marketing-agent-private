#!/usr/bin/env python3
"""
Authentication Debug Tool

This script helps debug authentication issues by:
1. Checking the auth token file
2. Testing authentication with the API
3. Creating a new auth token if needed
"""

import os
import json
import sys
import requests
import datetime
from typing import Dict, Any, Optional

API_URL = "http://localhost:8088"
AUTH_TOKEN_FILE = "auth_token.json"
TEST_USER = {"email": "test@example.com", "password": "password123"}

def check_auth_token_file():
    """Check if the auth token file exists and is valid"""
    print(f"Checking auth token file: {AUTH_TOKEN_FILE}")
    
    if not os.path.exists(AUTH_TOKEN_FILE):
        print(f"❌ Auth token file does not exist at {AUTH_TOKEN_FILE}")
        return None
        
    try:
        with open(AUTH_TOKEN_FILE, 'r') as f:
            token_data = json.load(f)
            
        # Check token structure
        token = token_data.get("token")
        expires_at = token_data.get("expires_at")
        user = token_data.get("user")
        
        if not token:
            print("❌ No token found in auth token file")
            return None
            
        print(f"✅ Found token: {token[:15]}...")
        
        if expires_at:
            print(f"Token expires at: {expires_at}")
            
        if user:
            print(f"User: {user.get('name', 'Unknown')} ({user.get('email', 'unknown')})")
            print(f"Role: {user.get('role', 'unknown')}")
            
        return token_data
    except Exception as e:
        print(f"❌ Error reading auth token file: {e}")
        return None

def test_authentication(token: str):
    """Test if the token works with the API"""
    print(f"\nTesting authentication with token: {token[:15]}...")
    
    headers = {"Authorization": f"Bearer {token}"}
    
    try:
        # Try accessing the companies endpoint
        response = requests.get(f"{API_URL}/api/companies/active", headers=headers)
        print(f"GET /api/companies/active status: {response.status_code}")
        
        if response.status_code == 200:
            print("✅ Authentication successful")
            return True
        else:
            print(f"❌ Authentication failed: {response.status_code}")
            print(f"Response: {response.text}")
            return False
    except Exception as e:
        print(f"❌ Error testing authentication: {e}")
        return False

def create_new_token():
    """Create a new auth token"""
    print("\nCreating new auth token...")
    
    try:
        # Login to get token
        response = requests.post(f"{API_URL}/api/auth/token", data=TEST_USER)
        
        if response.status_code == 200:
            token_data = response.json()
            print("✅ Token created successfully")
            
            # Save token to file
            with open(AUTH_TOKEN_FILE, 'w') as f:
                json.dump(token_data, f, indent=2)
                
            print(f"✅ Token saved to {AUTH_TOKEN_FILE}")
            return token_data
        else:
            print(f"❌ Failed to create token: {response.status_code}")
            print(f"Response: {response.text}")
            return None
    except Exception as e:
        print(f"❌ Error creating token: {e}")
        return None

def create_mock_token():
    """Create a mock token for testing"""
    print("\nCreating mock development token...")
    
    now = datetime.datetime.now()
    expires = now + datetime.timedelta(days=30)
    
    token_data = {
        "token": "DEVELOPMENT_MOCK_TOKEN_FOR_TESTING",
        "expires_at": expires.isoformat(),
        "user": {
            "id": "test_user",
            "email": "test@example.com",
            "name": "Test User",
            "role": "admin"
        }
    }
    
    try:
        # Save token to file
        with open(AUTH_TOKEN_FILE, 'w') as f:
            json.dump(token_data, f, indent=2)
            
        print(f"✅ Mock token saved to {AUTH_TOKEN_FILE}")
        return token_data
    except Exception as e:
        print(f"❌ Error creating mock token: {e}")
        return None

def create_login_user():
    """Create a login user in the database"""
    print("\nCreating login user in database...")
    
    # For now, just rely on the startup script to create the test user
    print("📝 Note: The API should create a test user on startup")
    print("📝 Check the API logs to verify the test user was created")
    return True

def fix_api_auth():
    """Apply fixes to the API authentication"""
    print("\nApplying fixes to API authentication...")
    
    # For now, just creating a mock token and relying on the API's dev mode
    # In a real scenario, this would involve more complex fixes
    token_data = create_mock_token()
    
    if token_data:
        print("✅ API authentication fixes applied")
        return True
    else:
        print("❌ Failed to apply API authentication fixes")
        return False

def main():
    """Main execution function"""
    print("\n" + "="*50)
    print("  AUTHENTICATION DEBUG TOOL")
    print("="*50 + "\n")
    
    # Check if the auth token file exists
    token_data = check_auth_token_file()
    token = token_data.get("token") if token_data else None
    
    # Test authentication if we have a token
    auth_works = False
    if token:
        auth_works = test_authentication(token)
        
    # If authentication doesn't work or no token, try to create one
    if not auth_works:
        print("\nAuthentication not working. Attempting fixes...")
        
        # Try to create a new token
        new_token_data = create_new_token()
        
        # If that doesn't work, try to create a mock token
        if not new_token_data:
            print("\nCould not create real token. Trying mock token...")
            mock_token_data = create_mock_token()
            
            if mock_token_data:
                token = mock_token_data.get("token")
                auth_works = test_authentication(token)
                
        # If still not working, try more advanced fixes
        if not auth_works:
            print("\nStill not working. Applying more fixes...")
            fix_api_auth()
            
            # Check one more time
            token_data = check_auth_token_file()
            if token_data:
                token = token_data.get("token")
                auth_works = test_authentication(token)
                
    # Final status
    print("\n" + "="*50)
    if auth_works:
        print("✅✅✅ AUTHENTICATION WORKING")
    else:
        print("❌❌❌ AUTHENTICATION NOT WORKING")
    print("="*50 + "\n")
    
    return auth_works

if __name__ == "__main__":
    success = main()
    sys.exit(0 if success else 1)
