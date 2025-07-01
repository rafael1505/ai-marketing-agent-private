#!/usr/bin/env python3
"""
Test updating brand colors
"""

import requests
import json
import sys

API_BASE_URL = "http://127.0.0.1:8088"
AUTH_HEADER = {"Authorization": "Bearer DEVELOPMENT_MOCK_TOKEN_FOR_TESTING"}

TEST_COLORS = ["#FF0000", "#00FF00", "#0000FF"]  # Red, Green, Blue

def test_update_brand_colors():
    print("=== TESTING BRAND COLORS UPDATE ===\n")
    
    # First get current company data
    try:
        response = requests.get(
            f"{API_BASE_URL}/api/v1/companies/active",
            headers=AUTH_HEADER,
            proxies={"http": None, "https": None}
        )
        
        if response.status_code != 200:
            print(f"❌ Failed to get company: {response.status_code}")
            print(response.text)
            return False
        
        company = response.json()
        company_id = company.get("id")
        
        if not company_id:
            print("❌ Company has no ID!")
            return False
            
        print(f"Company found: {company.get('name')}")
        print(f"Current brand colors: {company.get('brand_colors')}")
        
        # Now update the brand colors
        print(f"\nUpdating brand colors to: {TEST_COLORS}")
        
        # Two options to test:
        
        # Option 1: Send as FormData with JSON array
        form_data = {
            'name': company.get('name'),
            'brand_colors_json': json.dumps(TEST_COLORS)
        }
        
        # Option 2: Send as FormData with individual colors
        # Uncomment to test this approach
        """
        form_data = {
            'name': company.get('name'),
        }
        
        for i, color in enumerate(TEST_COLORS):
            form_data[f'brand_colors[{i}]'] = color
        """
        
        response = requests.put(
            f"{API_BASE_URL}/api/v1/companies/{company_id}",
            data=form_data,
            headers=AUTH_HEADER,
            proxies={"http": None, "https": None}
        )
        
        if response.status_code != 200:
            print(f"❌ Update failed: {response.status_code}")
            print(response.text)
            return False
        
        updated = response.json()
        
        if updated.get("company"):  # Check for nested company object
            updated_company = updated.get("company")
        else:
            updated_company = updated
            
        print("✅ Update call successful")
        print(f"Updated brand colors (from response): {updated_company.get('brand_colors')}")
        
        # Verify by fetching again
        print("\nVerifying by fetching company data...")
        response = requests.get(
            f"{API_BASE_URL}/api/v1/companies/active",
            headers=AUTH_HEADER,
            proxies={"http": None, "https": None}
        )
        
        if response.status_code != 200:
            print(f"❌ Verification failed: {response.status_code}")
            print(response.text)
            return False
        
        final = response.json()
        final_colors = final.get('brand_colors', [])
        
        print(f"Brand colors after fetch: {final_colors}")
        
        # Check if the colors match what we sent
        colors_match = sorted(final_colors) == sorted(TEST_COLORS)
        print(f"\nColors match: {'✓' if colors_match else '✗'}")
        
        if not colors_match:
            print(f"  Expected: {sorted(TEST_COLORS)}")
            print(f"  Actual:   {sorted(final_colors)}")
            
        return colors_match
        
    except Exception as e:
        print(f"❌ Error: {e}")
        return False

if __name__ == "__main__":
    if test_update_brand_colors():
        print("\n✅ TEST PASSED: Brand colors updated successfully")
        sys.exit(0)
    else:
        print("\n❌ TEST FAILED: Brand colors not updated correctly")
        sys.exit(1)
