import requests
import traceback
import sys
import json
import time

def test_company_persistence():
    base_url = "http://127.0.0.1:8088"

    print("Testing company persistence fix")
    print("-------------------------------")

    # Step 1: Get current company
    print("1. Getting current company...")
    response = requests.get(f"{base_url}/api/v1/companies/active", 
                            proxies={"http": None, "https": None})

    if response.status_code != 200:
        print(f"Failed to get company: {response.status_code}")
        print(response.text)
        return

    company = response.json()
    print(f"Current company: {company['name']}")
    print(f"Current colors: {company.get('brand_colors', [])}")

    company_id = company['id']

    # Step 2: Send update directly to API debug endpoint
    print("\n2. Attempting direct update via debug endpoint...")
    test_colors = ["#FF5500", "#00FF55"]

    update_data = {
        'name': f'Test Company Updated {time.time()}',
        'description': 'Updated via debug endpoint',
        'brand_colors': test_colors
    }

    response = requests.put(f"{base_url}/api-debug/{company_id}",
                            json=update_data,
                            proxies={"http": None, "https": None})

    print(f"Update status: {response.status_code}")
    if response.status_code != 200:
        print(f"Error response: {response.text}")
        return

    updated_company = response.json()
    print(f"Updated name: {updated_company['name']}")
    print(f"Updated colors: {updated_company.get('brand_colors', [])}")

    # Step 3: Check if data persisted by retrieving it again
    print("\n3. Checking if changes persisted...")
    time.sleep(1)  # Brief pause to ensure changes are saved

    response = requests.get(f"{base_url}/api/v1/companies/active",
                            proxies={"http": None, "https": None})

    if response.status_code != 200:
        print(f"Failed to get company: {response.status_code}")
        print(response.text)
        return

    final_company = response.json()
    print(f"Retrieved company name: {final_company['name']}")
    print(f"Retrieved colors: {final_company.get('brand_colors', [])}")

    # Check if changes persisted
    name_changed = updated_company['name'] == final_company['name']
    colors_changed = set(updated_company.get('brand_colors', [])) == set(final_company.get('brand_colors', []))

    print(f"\nResults:")
    print(f"Name persisted correctly: {name_changed}")
    print(f"Colors persisted correctly: {colors_changed}")

    if name_changed and colors_changed:
        print("✅ PERSISTENCE FIX SUCCESSFUL - Changes correctly saved and retrieved!")
    else:
        print("⚠️  PERSISTENCE ISSUE REMAINS - Changes did not persist correctly")

if __name__ == "__main__":
    try:
        test_company_persistence()
    except Exception as e:
        print(f"ERROR: {str(e)}")
        print(traceback.format_exc())
        sys.exit(1)
