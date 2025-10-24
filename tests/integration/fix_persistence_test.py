#!/usr/bin/env python3
"""
Focused test to fix company data persistence issue
"""
import requests
import json
import time
import os

API_BASE_URL = "http://127.0.0.1:8088/api/v1"
# Use the correct development mock token expected by the auth system
DEV_TOKEN = "DEVELOPMENT_MOCK_TOKEN"

# Disable any proxies for local testing
os.environ['NO_PROXY'] = '127.0.0.1,localhost'
# Configure requests to not use any proxies for our local calls
PROXIES = {
    'http': None,
    'https': None,
}

def get_current_company():
    """Get the current company data"""
    print("📋 Getting current company data...")
    try:
        print(f"   Requesting: GET {API_BASE_URL}/companies/active")
        response = requests.get(f"{API_BASE_URL}/companies/active", timeout=10, proxies=PROXIES)
        print(f"   Response status code: {response.status_code}")
        print(f"   Response headers: {response.headers}")
        
        if response.status_code == 200:
            data = response.json()
            print(f"   Company: {data.get('name', 'Unknown')}")
            print(f"   Colors: {data.get('brand_colors', [])}")
            print(f"   Email: {data.get('email', 'None')}")
            return data
        else:
            print(f"   ❌ Failed: {response.status_code} - {response.text}")
            return None
    except Exception as e:
        print(f"   ❌ Error: {e}")
        import traceback
        traceback.print_exc()
        return None

def update_company_with_formdata():
    """Update company using FormData (the working method)"""
    print("\n🔄 Updating company with FormData...")
    
    headers = {
        "Authorization": f"Bearer {DEV_TOKEN}"
    }
    
    # Use FormData with required fields
    # Using indexed format for brand_colors as expected by our backend fix
    data = {
        "name": "PERSISTENCE TEST Company",  # Updated name
        "description": "Testing persistence fix",
        "email": "persistence@test.com",  # Updated email
        "phone": "+1-555-PERSISTENCE",
        "address": "123 Persistence Street",
        "brand_colors[0]": "#FF1234",  # Red - NEW COLORS
        "brand_colors[1]": "#12FF34",  # Green
        "brand_colors[2]": "#1234FF",  # Blue
    }
    
    try:
        print(f"   Using auth token: {DEV_TOKEN}")
        response = requests.put(
            f"{API_BASE_URL}/companies/test_company",
            headers=headers,
            data=data,
            proxies=PROXIES,
            timeout=15
        )
        
        print(f"   Status: {response.status_code}")
        if response.status_code == 200:
            result = response.json()
            print(f"   ✅ Update successful!")
            print(f"   Updated Name: {result.get('name', 'Unknown')}")
            print(f"   Updated Colors: {result.get('brand_colors', [])}")
            print(f"   Updated Email: {result.get('email', 'None')}")
            return result
        else:
            print(f"   ❌ Update failed: {response.text}")
            return None
            
    except Exception as e:
        print(f"   ❌ Update error: {e}")
        return None

def test_persistence():
    """Test if changes persist after update"""
    print("\n🔍 Testing persistence...")
    
    # Step 1: Get initial state
    initial_company = get_current_company()
    if not initial_company:
        print("❌ Cannot get initial company state")
        return False
        
    # Step 2: Update company
    updated_company = update_company_with_formdata()
    if not updated_company:
        print("❌ Update failed")
        return False
    
    # Step 3: Wait a moment and check persistence
    print("\n⏳ Waiting 3 seconds for database write...")
    time.sleep(3)
    
    # Step 4: Get final state
    print("\n🔍 Verifying persistence...")
    final_company = get_current_company()
    if not final_company:
        print("❌ Cannot get final company state")
        return False
    
    # Step 5: Compare results
    print("\n📊 COMPARISON RESULTS:")
    print("-" * 40)
    
    # Check if name changed
    name_persisted = final_company.get('name') == "PERSISTENCE TEST Company"
    print(f"Name persistence: {'✅ SUCCESS' if name_persisted else '❌ FAILED'}")
    print(f"   Expected: PERSISTENCE TEST Company")
    print(f"   Actual: {final_company.get('name', 'None')}")
    
    # Check if colors changed
    expected_colors = ["#FF1234", "#12FF34", "#1234FF"]
    actual_colors = final_company.get('brand_colors', [])
    colors_persisted = actual_colors == expected_colors
    print(f"Colors persistence: {'✅ SUCCESS' if colors_persisted else '❌ FAILED'}")
    print(f"   Expected: {expected_colors}")
    print(f"   Actual: {actual_colors}")
    
    # Check if email changed
    email_persisted = final_company.get('email') == "persistence@test.com"
    print(f"Email persistence: {'✅ SUCCESS' if email_persisted else '❌ FAILED'}")
    print(f"   Expected: persistence@test.com")
    print(f"   Actual: {final_company.get('email', 'None')}")
    
    # Overall result
    all_persisted = name_persisted and colors_persisted and email_persisted
    print(f"\n🎯 OVERALL RESULT: {'✅ ALL DATA PERSISTED' if all_persisted else '❌ PERSISTENCE FAILED'}")
    
    if not all_persisted:
        print("\n🔧 DIAGNOSIS:")
        if not name_persisted:
            print("   - Name not persisting: possible form field issue")
        if not colors_persisted:
            print("   - Colors not persisting: array handling issue")
        if not email_persisted:
            print("   - Email not persisting: validation or save issue")
    
    return all_persisted

def main():
    print("🧪 Company Persistence Fix Test")
    print("=" * 50)
    
    # Run the persistence test
    success = test_persistence()
    
    print("\n" + "=" * 50)
    if success:
        print("🎉 SUCCESS: Company persistence is working!")
    else:
        print("🚨 FAILED: Company persistence needs fixing")
        print("\nNext steps:")
        print("1. Check database write operations in CompanyDB.update_company()")
        print("2. Verify FormData array parsing for brand_colors")
        print("3. Check if database connection is properly configured")
    
    return success

if __name__ == "__main__":
    print("Starting fix_persistence_test.py")
    try:
        main()
    except Exception as e:
        print(f"Error in main: {e}")
        import traceback
        traceback.print_exc()
