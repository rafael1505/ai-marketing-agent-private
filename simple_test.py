#!/usr/bin/env python3
import requests
import time
import uuid

# Configuration
BASE_URL = "http://127.0.0.1:8088"
AUTH_TOKEN = "DEVELOPMENT_MOCK_TOKEN_FOR_TESTING"
AUTH_HEADERS = {"Authorization": f"Bearer {AUTH_TOKEN}"}

def get_company():
    """Get active company"""
    try:
        response = requests.get(f"{BASE_URL}/api/v1/companies/active", headers=AUTH_HEADERS)
        if response.status_code == 200:
            data = response.json()
            print(f"Company retrieved: {data['name']}")
            print(f"Colors: {data.get('brand_colors', [])}")
            return data
        else:
            print(f"Error {response.status_code}: {response.text}")
            return None
    except Exception as e:
        print(f"Request error: {e}")
        return None

def update_company(company_id, new_colors):
    """Update company colors"""
    data = {
        "name": "Test Company",
        "description": "Simple color test"
    }
    
    # Add colors using array format
    for i, color in enumerate(new_colors):
        data[f"brand_colors[{i}]"] = color
    
    try:
        response = requests.put(
            f"{BASE_URL}/api/v1/companies/{company_id}",
            data=data,
            headers=AUTH_HEADERS
        )
        if response.status_code == 200:
            result = response.json()
            print(f"Update response colors: {result.get('brand_colors', [])}")
            return result
        else:
            print(f"Error {response.status_code}: {response.text}")
            return None
    except Exception as e:
        print(f"Update error: {e}")
        return None

def main():
    print("\n=== SIMPLE COMPANY COLOR PERSISTENCE TEST ===\n")
    
    # Get current company
    print("Step 1: Getting current company")
    company = get_company()
    if not company:
        print("Failed to get company")
        return
    company_id = company.get("id")
    
    # Generate unique test colors
    unique_id = uuid.uuid4().hex[:6]
    test_colors = [f"#{unique_id}1", f"#{unique_id}2"]
    print(f"\nStep 2: Updating with unique colors: {test_colors}")
    
    # Update company
    update_company(company_id, test_colors)
    
    # Delay to ensure changes are processed
    print("\nWaiting for changes to be processed...")
    time.sleep(1)
    
    # Get company again to verify persistence
    print("\nStep 3: Checking if colors persisted")
    updated_company = get_company()
    if not updated_company:
        print("Failed to get updated company")
        return
        
    # Check if colors match
    persisted_colors = updated_company.get("brand_colors", [])
    if sorted(persisted_colors) == sorted(test_colors):
        print("\n✓ SUCCESS! Colors were correctly persisted.")
    else:
        print("\n✗ FAILURE! Colors did not persist correctly.")
        print(f"  Expected: {test_colors}")
        print(f"  Got: {persisted_colors}")

if __name__ == "__main__":
    main()
