import requests
import json
import time

# Constants
BASE_URL = "http://127.0.0.1:8088"
AUTH_HEADER = {"Authorization": "Bearer DEVELOPMENT_MOCK_TOKEN_FOR_TESTING"}
COMPANY_ID = "test_company"

def check_api_connection():
    """Test if API is available"""
    try:
        response = requests.get(f"{BASE_URL}/api/v1/diagnostic/health")
        if response.status_code == 200:
            print("✅ API is running")
            return True
        else:
            print(f"❌ API returned status: {response.status_code}")
            return False
    except Exception as e:
        print(f"❌ API connection error: {e}")
        return False
        
def get_current_company():
    """Retrieve current company data"""
    try:
        response = requests.get(
            f"{BASE_URL}/api/v1/companies/active", 
            headers=AUTH_HEADER
        )
        if response.status_code == 200:
            data = response.json()
            print(f"Current company: {data['name']}")
            print(f"Current colors: {data.get('brand_colors', [])}")
            return data
        else:
            print(f"❌ Failed to get company: {response.status_code}")
            print(response.text)
            return None
    except Exception as e:
        print(f"❌ Error: {e}")
        return None
        
def update_company(company_id, name, description, colors):
    """Update company with new data"""
    print(f"\nUpdating company {company_id}...")
    data = {
        "name": name,
        "description": description,
    }
    
    # Add colors with array-style indices
    for i, color in enumerate(colors):
        data[f"brand_colors[{i}]"] = color
    
    try:
        response = requests.put(
            f"{BASE_URL}/api/v1/companies/{company_id}",
            data=data,
            headers=AUTH_HEADER
        )
        if response.status_code == 200:
            print(f"✅ Update successful")
            return True
        else:
            print(f"❌ Update failed: {response.status_code}")
            print(response.text)
            return False
    except Exception as e:
        print(f"❌ Error during update: {e}")
        return False

def test_persistence():
    """Test if updates persist"""
    if not check_api_connection():
        return False
        
    # Step 1: Get initial company data
    initial_company = get_current_company()
    if not initial_company:
        return False
        
    # Step 2: Update the company
    test_name = "Persistence Test Company"
    test_desc = "Testing if company data persists"
    test_colors = ["#FF0000", "#00FF00"]
    
    if not update_company(COMPANY_ID, test_name, test_desc, test_colors):
        return False
        
    # Step 3: Give the system a moment and then check if changes persisted
    print("\nWaiting to verify persistence...")
    time.sleep(1)
    
    # Step 4: Get updated company data
    updated_company = get_current_company()
    if not updated_company:
        return False
        
    # Step 5: Verify changes
    name_match = updated_company.get("name") == test_name
    colors_match = updated_company.get("brand_colors", []) == test_colors
    
    print(f"\nResults:")
    print(f"Name updated correctly: {name_match}")
    print(f"Colors updated correctly: {colors_match}")
    
    if name_match and colors_match:
        print("\n✅ SUCCESS: Company data persists correctly!")
        return True
    else:
        print("\n❌ FAILURE: Company data doesn't persist properly.")
        return False

if __name__ == "__main__":
    print("=== Company Persistence Test ===\n")
    test_persistence()
