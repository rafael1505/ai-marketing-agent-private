#!/usr/bin/env python3
import requests
import json
import time
import uuid

# Configuration
BASE_URL = "http://127.0.0.1:8088"
AUTH_HEADERS = {"Authorization": "Bearer DEVELOPMENT_MOCK_TOKEN_FOR_TESTING"}

def get_active_company():
    """Get the current active company"""
    response = requests.get(f"{BASE_URL}/api/v1/companies/active", headers=AUTH_HEADERS)
    if response.status_code == 200:
        return response.json()
    else:
        print(f"Error getting company: {response.status_code}")
        print(response.text)
        return None

def update_company_colors(company_id, colors):
    """Update just the company colors"""
    data = {}
    for i, color in enumerate(colors):
        data[f"brand_colors[{i}]"] = color
    
    # Add required fields
    data["name"] = "Test Company"
    data["description"] = "Testing color persistence"
    
    response = requests.put(
        f"{BASE_URL}/api/v1/companies/{company_id}",
        data=data,
        headers=AUTH_HEADERS
    )
    
    if response.status_code == 200:
        return response.json()
    else:
        print(f"Error updating company: {response.status_code}")
        print(response.text)
        return None

def main():
    print("=== Testing Brand Colors Persistence ===")
    
    # Get current company
    print("\n1. Getting current company")
    company = get_active_company()
    if not company:
        print("❌ Could not get company")
        return
    
    print(f"Current company: {company['name']}")
    print(f"Current colors: {company.get('brand_colors', [])}")
    company_id = company['id']
    
    # Generate unique test colors
    unique_id = uuid.uuid4().hex[:6]
    test_colors = [f"#{unique_id}1", f"#{unique_id}2"]
    print(f"\n2. Updating with unique colors: {test_colors}")
    
    # Update company
    updated = update_company_colors(company_id, test_colors)
    if not updated:
        print("❌ Update failed")
        return
    
    print(f"Update response colors: {updated.get('brand_colors', [])}")
    
    # Verify persistence
    print("\n3. Verifying persistence...")
    time.sleep(1)  # Brief delay to ensure changes are processed
    
    final = get_active_company()
    if not final:
        print("❌ Could not get updated company")
        return
    
    print(f"Retrieved company colors: {final.get('brand_colors', [])}")
    
    # Check if colors match
    stored_colors = final.get('brand_colors', [])
    if not stored_colors:
        print("❌ No colors found in final company")
    elif sorted(stored_colors) == sorted(test_colors):
        print("✅ SUCCESS: Colors were correctly persisted!")
    else:
        print("❌ FAILURE: Colors did not persist correctly")
        print(f"Expected: {test_colors}")
        print(f"Got: {stored_colors}")

if __name__ == "__main__":
    main()
