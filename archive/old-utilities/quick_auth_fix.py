#!/usr/bin/env python3

# Quick script to set up authentication token in browser localStorage
# This will make a token available for the frontend to use

import json
import os

def main():
    # Read the token from our auth_token.json file
    try:
        with open('auth_token.json', 'r') as f:
            token_data = json.load(f)
        
        token = token_data.get('access_token')
        if not token:
            print("❌ No access_token found in auth_token.json")
            return
        
        print("✅ Found valid authentication token")
        print(f"Token: {token[:30]}...")
        
        # Generate JavaScript to set the token in localStorage
        js_code = f"""
// Copy and paste this into your browser's console (F12) to set the auth token:
localStorage.setItem('token', '{token}');
console.log('✅ Authentication token set successfully!');
console.log('🔄 You can now refresh the page or navigate to settings to test.');
"""
        
        print("\n" + "="*70)
        print("BROWSER SETUP INSTRUCTIONS:")
        print("="*70)
        print("1. Open the application in your browser: http://localhost:3001")
        print("2. Press F12 to open Developer Tools")
        print("3. Go to the Console tab")
        print("4. Copy and paste this code:")
        print(js_code)
        print("5. Press Enter to execute")
        print("6. Navigate to Settings page to test company updates")
        print("="*70)
        
        return True
        
    except FileNotFoundError:
        print("❌ auth_token.json file not found")
        return False
    except json.JSONDecodeError:
        print("❌ Invalid JSON in auth_token.json")
        return False
    except Exception as e:
        print(f"❌ Error: {e}")
        return False

if __name__ == "__main__":
    main()
