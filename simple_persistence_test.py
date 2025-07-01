#!/usr/bin/env python3
"""
Simple test script for company persistence with authentication
"""

import sys
import os
sys.path.append(os.path.join(os.path.dirname(__file__)))

import requests
import json

# Disable proxy for local requests
proxies = {
    'http': None,
    'https': None,
}

def test_company_update():
    print("🧪 Testing Company Update with Authentication")
    print("=" * 50)
    
    # API Configuration
    API_BASE_URL = "http://127.0.0.1:8088/api/v1"
    COMPANY_ID = "test_company"
    DEV_TOKEN = "DEVELOPMENT_MOCK_TOKEN_12345"
    
    # Step 1: Get current company
    print("1. Getting current company...")
    try:
        response = requests.get(f"{API_BASE_URL}/companies/active", proxies=proxies)
        print(f"   Status: {response.status_code}")
        if response.status_code == 200:
            current_company = response.json()
            print(f"   Name: {current_company.get('name', 'Unknown')}")
            print(f"   Colors: {current_company.get('brand_colors', [])}")
        else:
            print(f"   Error: {response.text}")
            return False
    except Exception as e:
        print(f"   Exception: {e}")
        return False
    
    # Step 2: Update company with authentication
    print("\n2. Updating company with authentication...")
    headers = {
        "Authorization": f"Bearer {DEV_TOKEN}"
    }
    
    # Use form data as the API expects
    data = {
        "name": "Test Company UPDATED",
        "description": "This company was updated with authentication",
        "brand_colors[0]": "#FF0000",  # Red
        "brand_colors[1]": "#00FF00",  # Green
    }
    
    try:
        response = requests.put(
            f"{API_BASE_URL}/companies/{COMPANY_ID}",
            headers=headers,
            data=data,
            proxies=proxies
        )
        print(f"   Status: {response.status_code}")
        if response.status_code == 200:
            updated_company = response.json()
            print(f"   Updated Name: {updated_company.get('name', 'Unknown')}")
            print(f"   Updated Colors: {updated_company.get('brand_colors', [])}")
            print("   ✅ Update successful!")
        else:
            print(f"   Error: {response.text}")
            return False
    except Exception as e:
        print(f"   Exception: {e}")
        return False
    
    # Step 3: Verify persistence
    print("\n3. Verifying persistence...")
    try:
        response = requests.get(f"{API_BASE_URL}/companies/active", proxies=proxies)
        print(f"   Status: {response.status_code}")
        if response.status_code == 200:
            final_company = response.json()
            print(f"   Final Name: {final_company.get('name', 'Unknown')}")
            print(f"   Final Colors: {final_company.get('brand_colors', [])}")
            
            # Check if changes persisted
            name_changed = final_company.get('name') != current_company.get('name')
            colors_changed = final_company.get('brand_colors') != current_company.get('brand_colors')
            
            print(f"\n📊 Results:")
            print(f"   Name changed: {name_changed}")
            print(f"   Colors changed: {colors_changed}")
            
            if name_changed and colors_changed:
                print("   ✅ ALL CHANGES PERSISTED!")
                return True
            elif name_changed or colors_changed:
                print("   ⚠️  PARTIAL PERSISTENCE")
                return False
            else:
                print("   ❌ NO CHANGES PERSISTED")
                return False
        else:
            print(f"   Error: {response.text}")
            return False
    except Exception as e:
        print(f"   Exception: {e}")
        return False

if __name__ == "__main__":
    success = test_company_update()
    sys.exit(0 if success else 1)
