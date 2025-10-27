#!/usr/bin/env python3
"""
Script to generate and store a test token for developing and debugging
"""
from jose import jwt
from datetime import datetime, timedelta
import json

# Create a new token with a long expiration
token_data = {
    "sub": "1",
    "email": "test@example.com",
    "name": "Test User",
    "role": "admin",
    "is_admin": True,
    "iat": int(datetime.utcnow().timestamp()),
    "exp": int((datetime.utcnow() + timedelta(days=30)).timestamp())
}

# Sign the token
# Note: Secret key should match your app's SECRET_KEY in settings
SECRET_KEY = "thisisasecretkey" # This should match the key in app/core/config.py
signed_token = jwt.encode(token_data, SECRET_KEY, algorithm="HS256")

print(f"Generated test token: {signed_token[:30]}...")

# Save token to file
token_output = {
    "access_token": signed_token,
    "token_type": "bearer"
}

with open("auth_token_fresh.json", "w") as f:
    json.dump(token_output, f, indent=2)

# Also save raw token to a file for easier copying
with open("auth_token_new.txt", "w") as f:
    f.write(signed_token)

print(f"Token saved to auth_token_fresh.json and auth_token_new.txt")
print()
print("Instructions for using this token:")
print("1. Open auth-debug-suite.html in your browser")
print("2. Open the developer console (F12)")
print("3. Run: localStorage.setItem('token', '" + signed_token + "')")
print("4. Reload the page")
