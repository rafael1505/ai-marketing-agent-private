#!/usr/bin/env python3
"""
Simple test for company update after applying fixes
"""

import requests

def test_company_update():
    print("Testing company update after all fixes...")
    
    base_url = "http://127.0.0.1:8088"
    dev_token = "DEVELOPMENT_MOCK_TOKEN_FOR_TESTING"
    headers = {"Authorization": f"Bearer {dev_token}"}
    
    # Step 1: Get the active company
    print("\n1. Getting active company...")
    response = requests.get(
        f"{base_url}/api/v1/companies/active", 
        headers=headers,
        proxies={"http": None, "https": None}
    )
    
    if response.status_code != 200:
        print(f"Failed to get test company: {response.status_code}")
        return
    
    company = response.json()
    print(f"Found company: {company['name']}")
    print(f"ID: {company.get('id')}, _id: {company.get('_id', 'N/A')}")
    print(f"Brand colors: {company.get('brand_colors', [])}")
    
    # Step 2: Update the company
    print("\n2. Updating company...")
    
    # Create test data with new name and colors
    update_data = {
        'name': 'FIXED Test Company',
        'description': 'This description confirms the persistence fix works',
    }
    
    # Add colors as simple repeated fields
    colors = ['#FF5733', '#33FF57', '#3357FF']
    for color in colors:
        update_data['brand_colors'] = color
    
    # Send update request
    company_id = company.get('id')
    response = requests.put(
        f"{base_url}/api/v1/companies/{company_id}",
        data=update_data,
        headers=headers,
        proxies={"http": None, "https": None}
    )
    
    if response.status_code != 200:
        print(f"Update failed: {response.status_code}")
        print(response.text)
        return
    
    update_result = response.json()
    print(f"Update successful")
    print(f"Updated name: {update_result['name']}")
    print(f"Updated colors: {update_result.get('brand_colors', [])}")
    
    # Step 3: Verify changes were saved
    print("\n3. Verifying persistence...")
    response = requests.get(
        f"{base_url}/api/v1/companies/active", 
        headers=headers,
        proxies={"http": None, "https": None}
    )
    
    if response.status_code != 200:
        print(f"Failed to get updated company: {response.status_code}")
        return
    
    final = response.json()
    print(f"Retrieved company: {final['name']}")
    print(f"Retrieved colors: {final.get('brand_colors', [])}")
    
    # Check if changes persisted
    name_persisted = final['name'] == update_data['name']
    colors_match = set(final.get('brand_colors', [])) == set(colors) 
    
    print("\nResults:")
    print(f"Name persisted correctly: {'✅ YES' if name_persisted else '❌ NO'}")
    print(f"Colors persisted correctly: {'✅ YES' if colors_match else '❌ NO'}")
    
    if name_persisted and colors_match:
        print("\n🎉 SUCCESS: Company persistence issue is FIXED!")
    else:
        print("\n⚠️ PROBLEM: Company persistence issue still exists!")

if __name__ == "__main__":
    test_company_update()
