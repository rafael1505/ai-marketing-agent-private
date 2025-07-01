#!/usr/bin/env python3
"""
Generate and save a valid test auth token for development use
"""

import jwt
import time
import json
import os
import sys

# Define token parameters for development
TOKEN_SECRET = "development_secret_key"  # In real app would be environment variable
TOKEN_VALIDITY_DAYS = 30  # Token valid for 30 days

def generate_test_token():
    """Generate a JWT token for testing purposes"""
    current_time = int(time.time())
    expiry_time = current_time + (TOKEN_VALIDITY_DAYS * 24 * 60 * 60)  # 30 days
    
    # Create token payload
    payload = {
        "sub": "test@example.com",  # Subject (usually user ID or email)
        "name": "Test User",
        "role": "admin",
        "iat": current_time,  # Issued at time
        "exp": expiry_time    # Expiry time
    }
    
    # Generate token
    token = jwt.encode(payload, TOKEN_SECRET, algorithm="HS256")
    
    return {
        "access_token": token,
        "token_type": "bearer",
        "expires_in": TOKEN_VALIDITY_DAYS * 24 * 60 * 60
    }

def save_token_to_file(token_data):
    """Save token data to a file for easy access"""
    # Save prettified JSON
    with open("auth_token.json", "w") as f:
        json.dump(token_data, f, indent=2)
    
    # Create a simple text version with just the token
    with open("auth_token.txt", "w") as f:
        f.write(token_data["access_token"])
    
    print(f"Token saved to auth_token.json and auth_token.txt")
    print(f"Token will expire in {TOKEN_VALIDITY_DAYS} days")

if __name__ == "__main__":
    try:
        token_data = generate_test_token()
        save_token_to_file(token_data)
        print("\nUse this token in the frontend by copying it to localStorage:")
        print("\nlocalStorage.setItem('token', '" + token_data["access_token"] + "');")
        print("\nOr use the following curl command to test the API:")
        print(f"\ncurl -H \"Authorization: Bearer {token_data['access_token']}\" http://localhost:8088/api/v1/diagnostic/auth-test")
    except Exception as e:
        print(f"Error generating token: {e}")
        print("You may need to install PyJWT: pip install PyJWT")
        sys.exit(1)
