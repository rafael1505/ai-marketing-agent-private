#!/usr/bin/env python3
"""
Simple API test to verify company data
"""

import requests
import sys

API_BASE_URL = "http://127.0.0.1:8088"
AUTH_HEADER = {"Authorization": "Bearer DEVELOPMENT_MOCK_TOKEN_FOR_TESTING"}

def test_company_api():
    print("=== TESTING COMPANY DATA API ===\n")
    
    try:
        # Get active company first
        print("Fetching active company...")
        response = requests.get(
            f"{API_BASE_URL}/api/v1/companies/active",
            headers=AUTH_HEADER,
            proxies={"http": None, "https": None}
        )
        
        if response.status_code != 200:
            print(f"❌ Failed to get active company: {response.status_code}")
            print(response.text)
            return False
        
        company = response.json()
        print(f"✅ Found active company: {company.get('name')}")
        print(f"Company ID: {company.get('id')}")
        print(f"Brand colors: {company.get('brand_colors')}")
        print(f"Logo URL: {company.get('logo_url')}")
        
        # Update company name
        print("\nUpdating company name...")
        test_name = f"Test Company {datetime.now().strftime('%H:%M:%S')}"
        update_data = {
            "name": test_name
        }
        
        response = requests.put(
            f"{API_BASE_URL}/api/v1/companies/{company.get('id')}",
            data=update_data,
            headers=AUTH_HEADER,
            proxies={"http": None, "https": None}
        )
        
        if response.status_code != 200:
            print(f"❌ Failed to update company: {response.status_code}")
            print(response.text)
            return False
            
        updated = response.json()
        if updated.get("company"):
            updated_company = updated.get("company")
        else:
            updated_company = updated
            
        print(f"✅ Updated company name to: {updated_company.get('name')}")
        
        # Verify update persisted
        print("\nVerifying update persisted...")
        response = requests.get(
            f"{API_BASE_URL}/api/v1/companies/active",
            headers=AUTH_HEADER,
            proxies={"http": None, "https": None}
        )
        
        if response.status_code != 200:
            print(f"❌ Failed to get company: {response.status_code}")
            print(response.text)
            return False
            
        final = response.json()
        print(f"Retrieved company name: {final.get('name')}")
        print(f"Retrieved brand colors: {final.get('brand_colors')}")
        
        name_matches = final.get('name') == test_name
        print(f"Name matches test value: {'✓' if name_matches else '✗'}")
        
        return name_matches
        
    except Exception as e:
        print(f"❌ Error during test: {e}")
        return False

if __name__ == "__main__":
    from datetime import datetime
    if test_company_api():
        print("\n✅ TEST PASSED!")
        sys.exit(0)
    else:
        print("\n❌ TEST FAILED!")
        sys.exit(1)
