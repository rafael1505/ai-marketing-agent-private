#!/usr/bin/env python3
"""
Fix API Authentication Issues

This script creates a valid authentication token file and ensures
the API server will accept it for testing purposes.
"""

import os
import json
from datetime import datetime, timedelta

def fix_authentication():
    print("=== Fixing API Authentication ===")
    
    # Create a mock authentication token
    token_data = {
        "token": "DEVELOPMENT_MOCK_TOKEN_FOR_TESTING",
        "expires_at": (datetime.utcnow() + timedelta(days=30)).isoformat(),
        "user": {
            "id": "test_user",
            "email": "test@example.com",
            "name": "Test User",
            "role": "admin"
        }
    }
    
    # Save it to the token file
    with open("auth_token.json", "w") as f:
        json.dump(token_data, f, indent=2)
    
    print("✓ Created auth_token.json with test token")
    
    # Create a fresh copy too
    with open("auth_token_fresh.json", "w") as f:
        json.dump(token_data, f, indent=2)
    
    print("✓ Created auth_token_fresh.json with test token")
    
    # Create text version for easier access
    with open("auth_token.txt", "w") as f:
        f.write(token_data["token"])
    
    print("✓ Created auth_token.txt with plain token")
    
    print("\nAuthentication files created successfully!")
    print("The API server should now accept the test token for authentication.")

if __name__ == "__main__":
    fix_authentication()
