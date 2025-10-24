import requests
import json
import os

def test_company_update():
    base_url = "http://127.0.0.1:8088"
    
    # Add development auth token for testing
    dev_token = "DEVELOPMENT_MOCK_TOKEN_FOR_TESTING"
    headers = {"Authorization": f"Bearer {dev_token}"}
    
    # Step 1: Get current company
    print("Getting current company...")
    response = requests.get(f"{base_url}/api/v1/companies/active", 
                          proxies={"http": None, "https": None},
                          headers=headers)
    
    if response.status_code != 200:
        print(f"Failed to get company: {response.status_code}")
        print(response.text)
        return
    
    company = response.json()
    print(f"Current company: {company['name']}")
    print(f"Current colors: {company.get('brand_colors', [])}")
    print(f"Company ID: {company.get('id')}")
    print(f"Company _id (if present): {company.get('_id')}")
    
    # Now try to get the test company directly
    print("\nTrying to get test_company explicitly...")
    response = requests.get(f"{base_url}/api/v1/companies/test_company", 
                          proxies={"http": None, "https": None},
                          headers=headers)
    
    if response.status_code == 200:
        test_company = response.json()
        print(f"Found test_company: {test_company['name']}")
        print(f"test_company ID: {test_company.get('id')}")
    else:
        print(f"Failed to get test_company: {response.status_code}")
        print(response.text)
    
    company_id = company['id']
    
    # Step 2: Try to update with proper authentication
    print(f"\nTrying to update company {company_id}...")
    
    # Always use test_company as the ID
    company_id = "test_company"
    print(f"Using fixed ID 'test_company' instead of '{company.get('id')}'")
    
    # Create form data for multipart/form-data request (matches frontend)
    update_data = {
        'name': 'UPDATED Test Company',
        'description': 'Updated description',
        'email': company.get('email', ''),
        'phone': company.get('phone', ''),
        'address': company.get('address', ''),
        'logo_url': company.get('logo_url', '')
    }
    
    # Add brand colors as individual form fields with array indices
    colors = ['#AA0000', '#00AA00']
    for i, color in enumerate(colors):
        update_data[f'brand_colors[{i}]'] = color
    
    # Send request with auth headers
    response = requests.put(f"{base_url}/api/v1/companies/{company_id}",
                          data=update_data,
                          headers=headers,
                          proxies={"http": None, "https": None})
    
    print(f"Update status: {response.status_code}")
    print(f"Update response: {response.text[:500]}")
    
    # Step 3: Check if data persisted
    print("\nChecking persistence...")
    response = requests.get(f"{base_url}/api/v1/companies/active",
                          proxies={"http": None, "https": None})
    
    if response.status_code == 200:
        final_company = response.json()
        print(f"Final company: {final_company['name']}")
        print(f"Final colors: {final_company.get('brand_colors', [])}")
        
        # Check if changes persisted
        name_changed = company['name'] != final_company['name']
        colors_changed = company.get('brand_colors', []) != final_company.get('brand_colors', [])
        
        print(f"\nResults:")
        print(f"Name changed: {name_changed}")
        print(f"Colors changed: {colors_changed}")
        
        if not name_changed and not colors_changed:
            print("⚠️  NO CHANGES PERSISTED - This confirms the persistence issue!")
        else:
            print("✅ Changes persisted correctly")
    
if __name__ == "__main__":
    test_company_update()
