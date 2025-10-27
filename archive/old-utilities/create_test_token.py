#!/usr/bin/env python3

import sys
import os
from datetime import datetime, timedelta

# Add the project root to the Python path
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from app.core.auth import create_access_token

def create_test_token():
    """Create a test token for API access"""
    # Create token with test user data
    test_user_data = {
        "sub": "test_user_123",
        "email": "test@example.com", 
        "name": "Test User",
        "company_id": "demo_company_123"
    }
    
    # Create token with long expiration
    access_token_expires = timedelta(days=30)
    token = create_access_token(
        data=test_user_data,
        expires_delta=access_token_expires
    )
    
    print("Test token created:")
    print(token)
    print(f"\nUsage:")
    print(f'curl -H "Authorization: Bearer {token}" http://127.0.0.1:8088/api/v1/materials')
    
    return token

if __name__ == "__main__":
    create_test_token()
