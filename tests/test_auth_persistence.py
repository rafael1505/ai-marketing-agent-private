#!/usr/bin/env python3
"""
Test script to verify company persistence with proper authentication
"""

import requests
import json

# API Configuration
API_BASE_URL = "http://127.0.0.1:8088/api/v1"
COMPANY_ID = "test_company"

# Development mock token (matches what's expected in auth_fix.py)
DEV_TOKEN = "DEVELOPMENT_MOCK_TOKEN_12345"

def test_authentication():
    """Test that authentication works properly"""
    print("Testing authentication...")
    
    headers = {
        "Authorization": f"Bearer {DEV_TOKEN}",
        "Content-Type": "application/json"
    }
    
    # Try to access an authenticated endpoint
    response = requests.get(f"{API_BASE_URL}/companies/active", headers=headers)
    print(f"Auth test status: {response.status_code}")
    
    if response.status_code == 200:
        print("✅ Authentication working!")
        return True
    else:
        print(f"❌ Authentication failed: {response.text}")
        return False

def get_current_company():
    """Get current company data"""
    response = requests.get(f"{API_BASE_URL}/companies/active")
    if response.status_code == 200:
        return response.json()
    return None

def update_company_with_auth():
    """Update company with proper authentication"""
    headers = {
        "Authorization": f"Bearer {DEV_TOKEN}"
    }
    
    # Create form data like the frontend does
    data = {
        "name": "Test Company Updated",
        "description": "This is an updated test company",
        "email": "updated@test.com",
        "phone": "555-0123",
        "address": "123 Test Street",
        "brand_colors[0]": "#FF0000",  # Red
        "brand_colors[1]": "#00FF00",  # Green
    }
    
    response = requests.put(
        f"{API_BASE_URL}/companies/{COMPANY_ID}",
        headers=headers,
        data=data
    )
    
    return response

def main():
    print("🧪 Testing Company Persistence with Authentication")
    print("=" * 50)
    
    # Test 1: Authentication
    if not test_authentication():
        print("❌ Cannot proceed without authentication")
        return
    
    # Test 2: Get initial state
    print("\nGetting current company...")
    initial_company = get_current_company()
    if initial_company:
        print(f"Current company: {initial_company.get('name', 'Unknown')}")
        print(f"Current colors: {initial_company.get('brand_colors', [])}")
    else:
        print("❌ Could not fetch company")
        return
    
    # Test 3: Update with authentication
    print(f"\nTrying to update company {COMPANY_ID} with authentication...")
    response = update_company_with_auth()
    print(f"Update status: {response.status_code}")
    
    if response.status_code != 200:
        print(f"Update response: {response.text}")
        print("❌ Update failed even with authentication")
        return
    else:
        print("✅ Update successful!")
        updated_data = response.json()
        print(f"Updated company: {updated_data.get('name', 'Unknown')}")
        print(f"Updated colors: {updated_data.get('brand_colors', [])}")
    
    # Test 4: Verify persistence
    print("\nChecking persistence...")
    final_company = get_current_company()
    if final_company:
        print(f"Final company: {final_company.get('name', 'Unknown')}")
        print(f"Final colors: {final_company.get('brand_colors', [])}")
        
        # Check if changes persisted
        name_changed = final_company.get('name') != initial_company.get('name')
        colors_changed = final_company.get('brand_colors') != initial_company.get('brand_colors')
        
        print(f"\nResults:")
        print(f"Name changed: {name_changed}")
        print(f"Colors changed: {colors_changed}")
        
        if name_changed and colors_changed:
            print("✅ ALL CHANGES PERSISTED - Issue resolved!")
        elif name_changed or colors_changed:
            print("⚠️  PARTIAL PERSISTENCE - Some changes saved")
        else:
            print("❌ NO CHANGES PERSISTED - Issue still exists")
    else:
        print("❌ Could not fetch final company state")

if __name__ == "__main__":
    main()
