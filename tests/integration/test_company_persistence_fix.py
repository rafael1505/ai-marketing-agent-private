#!/usr/bin/env python3
"""
Test script to verify company persistence fixes.
This script will test the persistence of company data including brand colors.
"""
import requests
import json
from datetime import datetime

def test_company_update():
    base_url = "http://127.0.0.1:8088"
    
    print("\n===== COMPANY PERSISTENCE TEST =====\n")
    
    # Step 1: Get current company
    print("1. Fetching current company...")
    response = requests.get(f"{base_url}/api/v1/companies/active", 
                          proxies={"http": None, "https": None})
    
    if response.status_code != 200:
        print(f"ERROR: Failed to get company - {response.status_code}")
        print(response.text)
        return
    
    company = response.json()
    print(f"✅ Current company: {company['name']}")
    print(f"   Brand colors: {company.get('brand_colors', [])}")
    
    company_id = company['id']
    
    # Generate unique test data
    test_suffix = datetime.now().strftime("%H%M%S")
    test_name = f"Test Company {test_suffix}"
    test_desc = f"Test description {test_suffix}"
    test_colors = ["#FF0000", "#00FF00", "#0000FF"]  # Red, Green, Blue
    
    # Step 2: Update company with test data
    print(f"\n2. Updating company {company_id} with test data...")
    update_data = {
        'name': test_name,
        'description': test_desc,
        'email': company.get('email', 'test@example.com'),  # Use a valid email
        'phone': company.get('phone', ''),
        'address': company.get('address', ''),
        'logo_url': company.get('logo_url', ''),
        'brand_colors': test_colors
    }
    
    # Get a token for authentication
    # In a real test we would use real auth
    # For this test we're using the development token
    token = "eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9.eyJzdWIiOiIxIiwiZXhwIjoxNzUwODU3ODc2fQ.LG-EpDaoAgH0ih_Weo0p50qo8c3YXT-ZKtOT-W2GD8Q"
    
    headers = {
        'Authorization': f'Bearer {token}'
    }
    
    # Remove empty fields
    update_data = {k: v for k, v in update_data.items() if v is not None and v != ''}
    
    # Handle brand_colors specially
    form_data = {}
    for key, value in update_data.items():
        if key != 'brand_colors':
            form_data[key] = value
    
    # Add brand colors with array indexing
    for idx, color in enumerate(update_data.get('brand_colors', [])):
        form_data[f'brand_colors[{idx}]'] = color
    
    print(f"   Sending form data: {form_data}")
    
    response = requests.put(f"{base_url}/api/v1/companies/{company_id}",
                          data=form_data,
                          headers=headers,
                          proxies={"http": None, "https": None})
    
    if response.status_code != 200:
        print(f"ERROR: Update failed - {response.status_code}")
        print(response.text[:500])
        return
        
    print(f"✅ Update successful!")
    update_response = response.json()
    print(f"   Response data: {update_response.get('message', '')}")
    if 'company' in update_response:
        updated_company = update_response['company']
        print(f"   Updated name: {updated_company.get('name')}")
        print(f"   Updated colors: {updated_company.get('brand_colors', [])}")
    
    # Step 3: Check if data persisted
    print("\n3. Verifying persistence by retrieving company again...")
    response = requests.get(f"{base_url}/api/v1/companies/active",
                          proxies={"http": None, "https": None})
    
    if response.status_code != 200:
        print(f"ERROR: Failed to get company after update - {response.status_code}")
        print(response.text)
        return
        
    final_company = response.json()
    print(f"✅ Company fetched successfully")
    print(f"   Name: {final_company['name']}")
    print(f"   Description: {final_company['description']}")
    print(f"   Brand colors: {final_company.get('brand_colors', [])}")
    
    # Check if changes persisted
    name_persisted = final_company['name'] == test_name
    desc_persisted = final_company['description'] == test_desc
    
    # For colors, check if all our test colors are present (order may differ)
    colors_persisted = all(color in final_company.get('brand_colors', []) for color in test_colors)
    color_count_correct = len(final_company.get('brand_colors', [])) == len(test_colors)
    
    print(f"\n===== TEST RESULTS =====")
    print(f"Name persisted correctly: {'✅ YES' if name_persisted else '❌ NO'}")
    print(f"Description persisted correctly: {'✅ YES' if desc_persisted else '❌ NO'}")
    print(f"Brand colors persisted correctly: {'✅ YES' if colors_persisted and color_count_correct else '❌ NO'}")
    
    if name_persisted and desc_persisted and colors_persisted and color_count_correct:
        print("\n✅✅✅ PERSISTENCE TEST PASSED ✅✅✅")
    else:
        print("\n❌❌❌ PERSISTENCE TEST FAILED ❌❌❌")

if __name__ == "__main__":
    test_company_update()
