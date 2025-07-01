import asyncio
import sys
import json
from app.core.auth import verify_password, get_password_hash

def test_auth():
    # Test password hashing and verification
    password = "password"
    hashed = get_password_hash(password)
    
    print(f"Original password: {password}")
    print(f"Hashed password: {hashed}")
    
    # Verify the password
    is_valid = verify_password(password, hashed)
    print(f"Password verification result: {is_valid}")
    
    # Verify with wrong password
    is_invalid = verify_password("wrongpassword", hashed)
    print(f"Invalid password verification result: {is_invalid}")

if __name__ == "__main__":
    try:
        print("Testing password verification...")
        test_auth()
        print("Test completed successfully")
    except Exception as e:
        import traceback
        print(f"An error occurred: {e}")
        print(traceback.format_exc())
