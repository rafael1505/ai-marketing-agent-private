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
    
    company_id = company['id']
    
    # Step 2: Try to update with proper authentication
    print(f"\nTrying to update company {company_id}...")
    
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
    
    # Let's sleep for a second to make sure any async operations complete
    import time
    time.sleep(1)
    
    # Step 3: Check if data persisted - use direct company ID endpoint
    print("\nChecking persistence...")
    # First fetch the specific company by ID rather than just the active company
    response = requests.get(f"{base_url}/api/v1/companies/{company_id}",
                          headers=headers,  # Include auth headers
                          proxies={"http": None, "https": None})
    
    if response.status_code != 200:
        print(f"Failed to get company by ID: {response.status_code}")
        print(response.text)
        
        # Try the active company endpoint as fallback
        response = requests.get(f"{base_url}/api/v1/companies/active",
                              headers=headers,  # Include auth headers
                              proxies={"http": None, "https": None})
    
    if response.status_code == 200:
        final_company = response.json()
        print(f"Final company: {final_company['name']}")
        print(f"Final colors: {final_company.get('brand_colors', [])}")
    else:
        print(f"Failed to fetch company data: {response.status_code}")
        print(response.text)
        return
    
    print("\nResults:")
    name_changed = final_company['name'] == "UPDATED Test Company"
    colors_changed = final_company.get('brand_colors', []) == ['#AA0000', '#00AA00']
    print(f"Name changed: {name_changed}")
    print(f"Colors changed: {colors_changed}")
    
    if not (name_changed and colors_changed):
        print("⚠️  NO CHANGES PERSISTED - This confirms the persistence issue!")
    else:
        print("✅ Changes persisted successfully!")

if __name__ == "__main__":
    test_company_update()
