#!/usr/bin/env python3
"""
Final API test with ID fix
"""
import requests
import json
import uuid
import time

# Configuration
BASE_URL = "http://127.0.0.1:8088" 
AUTH_TOKEN = "DEVELOPMENT_MOCK_TOKEN_FOR_TESTING"
AUTH_HEADERS = {"Authorization": f"Bearer {AUTH_TOKEN}"}

def test_company_persistence():
    print("=== Testing Company Persistence ===")
    
    # Step 1: Get active company
    print("\nStep 1: Getting active company")
    try:
        response = requests.get(f"{BASE_URL}/api/v1/companies/active", headers=AUTH_HEADERS)
        if response.status_code != 200:
            print(f"Error: {response.status_code} - {response.text}")
            return
        
        company = response.json()
        print(f"Company: {company['name']}")
        print(f"Colors: {company.get('brand_colors')}")
        
        # Extract IDs - we need both id and _id
        company_id = company.get("id")
        # For non-MongoDB, the ID might be in _id
        mongo_id = company.get("_id", company_id)
        print(f"Company ID: {company_id}")
        print(f"MongoDB ID: {mongo_id}")
        
        # Try using test_company ID as a special case
        special_id = "test_company"
        
        # Generate test data
        test_id = uuid.uuid4().hex[:6]
        test_name = f"Test Company {test_id}"
        test_colors = [f"#{test_id}1", f"#{test_id}2"]
        print(f"Test name: {test_name}")
        print(f"Test colors: {test_colors}")
        
        # Step 2: Try updating with different IDs
        print("\nStep 2: Updating company (trying multiple IDs)")
        
        # Method 1: Try using the reported ID
        print("\nTrying with company_id...")
        data = {
            "name": test_name,
            "description": "Testing with company_id"
        }
        for i, color in enumerate(test_colors):
            data[f"brand_colors[{i}]"] = color
            
        response = requests.put(
            f"{BASE_URL}/api/v1/companies/{company_id}",
            data=data,
            headers=AUTH_HEADERS
        )
        print(f"Status: {response.status_code}")
        if response.status_code == 200:
            print("Success!")
            updated = response.json()
            print(f"Updated company: {json.dumps(updated, indent=2)}")
        else:
            print(f"Failed: {response.text}")
            
            # Try with mongo_id if different
            if mongo_id and mongo_id != company_id:
                print("\nTrying with mongo_id...")
                response = requests.put(
                    f"{BASE_URL}/api/v1/companies/{mongo_id}",
                    data=data,
                    headers=AUTH_HEADERS
                )
                print(f"Status: {response.status_code}")
                if response.status_code == 200:
                    print("Success!")
                    updated = response.json()
                    print(f"Updated company: {json.dumps(updated, indent=2)}")
                else:
                    print(f"Failed: {response.text}")
            
            # Try with special test_company ID
            print("\nTrying with test_company special ID...")
            response = requests.put(
                f"{BASE_URL}/api/v1/companies/{special_id}",
                data=data,
                headers=AUTH_HEADERS
            )
            print(f"Status: {response.status_code}")
            if response.status_code == 200:
                print("Success!")
                updated = response.json()
                print(f"Updated company: {json.dumps(updated, indent=2)}")
            else:
                print(f"Failed: {response.text}")
                
        # Step 3: Check if update persisted
        print("\nStep 3: Verifying persistence")
        time.sleep(1)
        response = requests.get(f"{BASE_URL}/api/v1/companies/active", headers=AUTH_HEADERS)
        if response.status_code == 200:
            final = response.json()
            print(f"Current company: {final.get('name')}")
            print(f"Current colors: {final.get('brand_colors')}")
            
            name_matches = final.get('name') == test_name
            colors_match = sorted(final.get('brand_colors') or []) == sorted(test_colors)
            
            print("\nResults:")
            print(f"Name updated: {name_matches}")
            print(f"Colors updated: {colors_match}")
            
            if name_matches and colors_match:
                print("\n✅ SUCCESS: Update persisted correctly!")
            else:
                print("\n⚠️ WARNING: Update did not persist fully")
        else:
            print(f"Error checking persistence: {response.status_code} - {response.text}")
            
    except Exception as e:
        print(f"Error: {e}")

if __name__ == "__main__":
    test_company_persistence()
