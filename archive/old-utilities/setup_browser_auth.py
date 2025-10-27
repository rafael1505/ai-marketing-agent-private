#!/usr/bin/env python3
"""
Quick Authentication Fix Script
This script provides instructions to set up authentication token in the browser
"""

import json
import os

# Read the authentication token from auth_token.json
token_file = "auth_token.json"
if os.path.exists(token_file):
    with open(token_file, 'r') as f:
        token_data = json.load(f)
        token = token_data.get('access_token')
else:
    token = None

print("🔧 Quick Authentication Fix")
print("=" * 50)

if not token:
    print("❌ Error: auth_token.json file not found!")
    print("Please ensure the backend server is running and has generated a token.")
    exit(1)

print("✅ Found authentication token!")
print(f"Token preview: {token[:20]}...")

print("\n📋 Browser Setup Instructions:")
print("1. Open your browser to http://localhost:3001")
print("2. Open Developer Tools (F12)")
print("3. Go to the Console tab")
print("4. Paste and run this command:")
print()
print(f"localStorage.setItem('token', '{token}');")
print()
print("5. Refresh the page")
print()
print("✅ After following these steps:")
print("- Authentication should work properly")
print("- Company data updates should save successfully")
print("- The UserMenu component should function correctly")

print("\n🚀 Alternative: Use the Auth Debug Suite")
print("Visit: http://localhost:3001/auth-debug-suite.html")
print("Click 'Use Dev Token' to automatically set up authentication")
