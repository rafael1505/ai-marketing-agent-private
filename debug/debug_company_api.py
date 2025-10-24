#!/usr/bin/env python3
# filepath: /mnt/c/Users/brc07274/OneDrive - Philips/Philips Files/BU - CI/Repository/AI Marketing Agent (Python)/ai-marketing-agent/debug_company_api.py
import requests
import json
import os
import sys

"""
Advanced debugger for company API persistence issues
This script:
1. Retrieves a development auth token
2. Gets current company data
3. Attempts to update the company with the token
4. Verifies if the update persisted
"""

# Constants
API_BASE = "http://127.0.0.1:8088"
DEV_TOKEN = "DEVELOPMENT_MOCK_TOKEN_12345"  # This works with development environment

def get_company():
    """Get the current active company data"""
    print("Step 1: Getting current company...")
    response = requests.get(f"{API_BASE}/api/v1/companies/active", 
                          proxies={"http": None, "https": None})
    
    if response.status_code != 200:
        print(f"Failed to get company: {response.status_code}")
        print(response.text)
        return None
    
    company = response.json()
    print(f"Current company: {company['name']}")
    print(f"Current colors: {company.get('brand_colors', [])}")
    print(f"Company ID from API: {company['id']}")
    
    # CRITICAL FIX: Always use "test_company" as the ID for updates
    # regardless of what the API returns
    company['id'] = "test_company"
    print(f"Using ID for updates: {company['id']}")
    return company

def update_company_json(company_id, update_data):
    """Try updating company using JSON request (standard)"""
    print(f"\nStep 2A: Updating company {company_id} using JSON request with auth...")
    
    headers = {
        "Authorization": f"Bearer {DEV_TOKEN}",
        "Content-Type": "application/json"
    }
    
    response = requests.put(
        f"{API_BASE}/api/v1/companies/{company_id}",
        json=update_data,
        headers=headers,
        proxies={"http": None, "https": None}
    )
    
    print(f"JSON Update status: {response.status_code}")
    print(f"JSON Update response: {response.text[:500]}")
    return response.status_code == 200

def update_company_form(company_id, update_data):
    """Try updating company using form data (like the frontend)"""
    print(f"\nStep 2B: Updating company {company_id} using FormData with auth...")
    
    headers = {
        "Authorization": f"Bearer {DEV_TOKEN}"
    }
    
    # Test both array format approaches
    form_data = {}
    for key, value in update_data.items():
        if key == 'brand_colors' and isinstance(value, list):
            # First approach: Try sending multiple values with the same key name
            # FastAPI will interpret this as a list
            for color in value:
                form_data.setdefault('brand_colors', []).append(color)
        else:
            form_data[key] = value
    
    print("FormData being sent:", form_data)
    
    # Use requests' built-in ability to handle lists in form data
    response = requests.put(
        f"{API_BASE}/api/v1/companies/{company_id}",
        data=form_data,  # When a key has a list value, requests will create multiple form fields
        headers=headers,
        proxies={"http": None, "https": None}
    )
    
    print(f"FormData Update status: {response.status_code}")
    print(f"FormData Update response: {response.text[:500]}")
    return response.status_code == 200

def verify_update():
    """Check if update persisted"""
    print("\nStep 3: Verifying if update persisted...")
    company = get_company()
    if not company:
        return False
    
    # Check if the expected changes are present
    name_updated = "UPDATED" in company['name']
    colors_updated = "#AA0000" in company.get('brand_colors', []) and "#00AA00" in company.get('brand_colors', [])
    
    print(f"\nResults:")
    print(f"Name updated: {name_updated}")
    print(f"Colors updated: {colors_updated}")
    
    return name_updated and colors_updated

def main():
    # Step 1: Get current company
    company = get_company()
    if not company:
        print("Failed to get company. Exiting.")
        return
    
    company_id = company['id']
    
    # Prepare update data
    update_data = {
        'name': f'UPDATED Test Company {os.urandom(2).hex()}',  # Add random suffix to ensure change
        'description': 'Updated description for testing',
        'email': company.get('email', ''),
        'phone': company.get('phone', ''),
        'address': company.get('address', ''),
        'logo_url': company.get('logo_url', ''),
        'brand_colors': ['#AA0000', '#00AA00']
    }
    
    # Try both update methods
    json_success = update_company_json(company_id, update_data)
    
    if not json_success:
        print("\n⚠️ JSON update failed. Trying FormData method...")
        form_success = update_company_form(company_id, update_data)
        
        if not form_success:
            print("⚠️ Both update methods failed. There may be an issue with the API or authentication.")
            return
    
    # Verify the update worked
    persistence_success = verify_update()
    
    if persistence_success:
        print("\n✅ SUCCESS: Company update persisted correctly!")
    else:
        print("\n❌ FAILURE: Company update was not persisted correctly.")
        print("This confirms there's an issue with the persistence mechanism.")

if __name__ == "__main__":
    main()
