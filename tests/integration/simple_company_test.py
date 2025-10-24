#!/usr/bin/env python3

import requests
import json

def test_company_persistence():
    print("=== Simple Company Persistence Test ===\n")
    
    base_url = "http://127.0.0.1:8088"
    
    # Step 1: Get current company data
    print("1. Getting current company data...")
    try:
        response = requests.get(f"{base_url}/api/v1/companies/active", 
                              proxies={"http": None, "https": None})
        if response.status_code == 200:
            current_company = response.json()
            print(f"Current company: {json.dumps(current_company, indent=2)}")
            company_id = current_company.get('id')
        else:
            print(f"Failed to get company: {response.status_code} - {response.text}")
            return
    except Exception as e:
        print(f"Error getting company: {e}")
        return
    
    # Step 2: Update the company name
    print(f"\n2. Updating company {company_id}...")
    
    # Prepare form data for update
    update_data = {
        'name': 'UPDATED Philips Company',
        'description': 'This company has been updated via API test!',
        'email': current_company.get('email', ''),
        'phone': current_company.get('phone', ''),
        'address': current_company.get('address', ''),
        'logo_url': current_company.get('logo_url', ''),
        'brand_colors': ['#FF0000', '#00FF00', '#0000FF']  # New colors
    }
    
    try:
        # We need to authenticate for updates - let's try without auth first to see the error
        response = requests.put(f"{base_url}/api/v1/companies/{company_id}",
                              data=update_data,
                              proxies={"http": None, "https": None})
        print(f"Update response status: {response.status_code}")
        print(f"Update response: {response.text}")
        
        if response.status_code == 200:
            updated_company = response.json()
            print(f"Updated company: {json.dumps(updated_company, indent=2)}")
        
    except Exception as e:
        print(f"Error updating company: {e}")
    
    # Step 3: Get company data again to check persistence
    print("\n3. Checking if changes persisted...")
    try:
        response = requests.get(f"{base_url}/api/v1/companies/active",
                              proxies={"http": None, "https": None})
        if response.status_code == 200:
            final_company = response.json()
            print(f"Final company: {json.dumps(final_company, indent=2)}")
            
            # Compare
            print(f"\n4. Comparison:")
            print(f"Name changed: {current_company.get('name')} -> {final_company.get('name')}")
            print(f"Description changed: {current_company.get('description')} -> {final_company.get('description')}")
            print(f"Colors changed: {current_company.get('brand_colors')} -> {final_company.get('brand_colors')}")
            
        else:
            print(f"Failed to get final company: {response.status_code} - {response.text}")
    except Exception as e:
        print(f"Error getting final company: {e}")

if __name__ == "__main__":
    test_company_persistence()
