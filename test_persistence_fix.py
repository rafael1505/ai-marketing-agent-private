#!/usr/bin/env python3

import requests
import json

def test_company_endpoints():
    print("=== Testing Company Endpoints ===\n")
    
    base_url = "http://127.0.0.1:8088"
    company_id = "test_company"
    test_colors = ["#FF5533", "#33FF57"] # Test colors for updating
    
    # Step 1: Get current company info
    print("1. Getting current company info...")
    try:
        response = requests.get(f"{base_url}/api/v1/companies/{company_id}")
        print(f"GET Status: {response.status_code}")
        if response.status_code == 200:
            company_data = response.json()
            print(f"Current company data: {json.dumps(company_data, indent=2)}")
            current_name = company_data.get('name', 'Unknown')
            current_colors = company_data.get('brand_colors', [])
            print(f"Current name: {current_name}")
            print(f"Current colors: {current_colors}")
        else:
            print(f"Error response: {response.text}")
            return False
    except requests.exceptions.RequestException as e:
        print(f"GET request failed: {e}")
        return False
    
    # Step 2: Update the company with test data
    print("\n2. Updating company...")
    
    # Get an auth token (may need to adjust if your auth system is different)
    try:
        # Simplified test - using a mock token that should work in development mode
        auth_token = "DEVELOPMENT_MOCK_TOKEN_FOR_TESTING"
        headers = {"Authorization": f"Bearer {auth_token}"}
        
        # Prepare form data
        form_data = {
            'name': 'Updated Test Company',
            'description': 'This company has been updated by the test script',
        }
        
        # Add brand colors with proper indexing for FormData
        for i, color in enumerate(test_colors):
            form_data[f'brand_colors[{i}]'] = color
        
        # Send PUT request
        response = requests.put(
            f"{base_url}/api/v1/companies/{company_id}", 
            headers=headers,
            data=form_data
        )
        
        print(f"PUT Status: {response.status_code}")
        if response.status_code == 200:
            update_result = response.json()
            print(f"Update response: {json.dumps(update_result, indent=2)}")
        else:
            print(f"Update error: {response.text}")
            return False
    except requests.exceptions.RequestException as e:
        print(f"PUT request failed: {e}")
        return False
    
    # Step 3: Get company again to check if updates persisted
    print("\n3. Checking if updates persisted...")
    try:
        response = requests.get(f"{base_url}/api/v1/companies/{company_id}")
        print(f"GET Status: {response.status_code}")
        if response.status_code == 200:
            final_data = response.json()
            print(f"Final company data: {json.dumps(final_data, indent=2)}")
            
            # Verify changes
            new_name = final_data.get('name', 'Unknown')
            new_colors = final_data.get('brand_colors', [])
            
            print(f"Final name: {new_name}")
            print(f"Final colors: {new_colors}")
            
            # Check if changes persisted correctly
            name_changed = new_name == 'Updated Test Company'
            colors_changed = sorted(new_colors) == sorted(test_colors)
            
            print("\nResults:")
            print(f"Name changed: {name_changed}")
            print(f"Colors changed: {colors_changed}")
            
            if name_changed and colors_changed:
                print("✅ SUCCESS - Changes persisted correctly!")
            else:
                print("⚠️  FAILURE - Changes did not persist correctly!")
                
            return name_changed and colors_changed
        else:
            print(f"Error response: {response.text}")
            return False
    except requests.exceptions.RequestException as e:
        print(f"Final GET request failed: {e}")
        return False

if __name__ == "__main__":
    try:
        print("Starting test script...")
        result = test_company_endpoints()
        print(f"\nTest result: {'SUCCESS' if result else 'FAILURE'}")
    except Exception as e:
        import traceback
        print(f"\nTest failed with exception: {e}")
        traceback.print_exc()
        print("\nTest result: FAILURE (exception)")
