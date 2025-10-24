#!/usr/bin/env python3
"""
FormData test script that tests the company update endpoint with 
different content types and data formats
"""
import requests
import json
import time
import sys
from pprint import pprint

def test_formdata_company_update():
    """Test all variants of FormData submission to the company update endpoint"""
    # Check if active company endpoint is working first
    base_url = "http://127.0.0.1:8088"
    
    print("\n--- Testing API connection ---")
    try:
        response = requests.get(f"{base_url}/api/v1/companies/active", 
                              proxies={"http": None, "https": None},
                              timeout=5)
        print(f"API Status: {response.status_code}")
        if response.status_code == 200:
            print("API connection successful")
            company = response.json()
            print(f"Current company: {company['name']}")
        else:
            print("API connection failed")
            print(f"Error: {response.text}")
            sys.exit(1)
    except Exception as e:
        print(f"API connection error: {str(e)}")
        sys.exit(1)
    company_id = "test_company"
    test_url = f"{base_url}/api/v1/companies/{company_id}"
    
    # Get a mock token for authentication
    token = "eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9.eyJzdWIiOiIxIiwiZXhwIjoxNzUwODU3ODc2fQ.LG-EpDaoAgH0ih_Weo0p50qo8c3YXT-ZKtOT-W2GD8Q"
    auth_header = {"Authorization": f"Bearer {token}"}
    
    # Test case 1: JSON data
    print("\n--- Test 1: JSON Content Type ---")
    json_data = {
        "name": "Updated via JSON",
        "description": "Updated with JSON content type",
        "brand_colors": ["#FF5500", "#00FF55"]
    }
    
    response = requests.put(
        test_url, 
        json=json_data, 
        headers={
            **auth_header,
            "Content-Type": "application/json"
        },
        proxies={"http": None, "https": None}
    )
    
    print(f"Status: {response.status_code}")
    print(f"Response: {response.text[:500]}")
    print("\nVerifying update...")
    
    # Verify the update
    verify_response = requests.get(
        f"{base_url}/api/v1/companies/active",
        proxies={"http": None, "https": None}
    )
    
    if verify_response.status_code == 200:
        company = verify_response.json()
        print(f"Company name: {company.get('name')}")
        print(f"Brand colors: {company.get('brand_colors', [])}")
    
    time.sleep(1)  # Small delay between tests
    
    # Test case 2: FormData with direct fields
    print("\n--- Test 2: FormData with Direct Fields ---")
    form_data = {
        "name": "Updated via FormData",
        "description": "Updated with direct FormData fields",
        "brand_colors": json.dumps(["#5500FF", "#55FF00"])  # JSON encoded array
    }
    
    response = requests.put(
        test_url,
        data=form_data,
        headers={
            **auth_header,
            # Let the browser set the Content-Type with boundary
        },
        proxies={"http": None, "https": None}
    )
    
    print(f"Status: {response.status_code}")
    print(f"Response: {response.text[:500]}")
    print("\nVerifying update...")
    
    # Verify the update
    verify_response = requests.get(
        f"{base_url}/api/v1/companies/active",
        proxies={"http": None, "https": None}
    )
    
    if verify_response.status_code == 200:
        company = verify_response.json()
        print(f"Company name: {company.get('name')}")
        print(f"Brand colors: {company.get('brand_colors', [])}")
    
    time.sleep(1)  # Small delay between tests
    
    # Test case 3: FormData with indexed array notation
    print("\n--- Test 3: FormData with Indexed Array Notation ---")
    form_data = {
        "name": "Updated via FormData Arrays",
        "description": "Updated with indexed array notation",
        "brand_colors[0]": "#1122AA",
        "brand_colors[1]": "#22AA11"
    }
    
    response = requests.put(
        test_url,
        data=form_data,
        headers=auth_header,
        proxies={"http": None, "https": None}
    )
    
    print(f"Status: {response.status_code}")
    print(f"Response: {response.text[:500]}")
    print("\nVerifying update...")
    
    # Verify the update
    verify_response = requests.get(
        f"{base_url}/api/v1/companies/active",
        proxies={"http": None, "https": None}
    )
    
    if verify_response.status_code == 200:
        company = verify_response.json()
        print(f"Company name: {company.get('name')}")
        print(f"Brand colors: {company.get('brand_colors', [])}")
    
    time.sleep(1)  # Small delay between tests
    
    # Test case 4: FormData with comma-separated string
    print("\n--- Test 4: FormData with Comma-Separated String ---")
    form_data = {
        "name": "Updated via Comma List",
        "description": "Updated with comma-separated colors",
        "brand_colors": "#AA1122, #11AA22"  # Comma-separated string
    }
    
    response = requests.put(
        test_url,
        data=form_data,
        headers=auth_header,
        proxies={"http": None, "https": None}
    )
    
    print(f"Status: {response.status_code}")
    print(f"Response: {response.text[:500]}")
    print("\nVerifying update...")
    
    # Verify the update
    verify_response = requests.get(
        f"{base_url}/api/v1/companies/active",
        proxies={"http": None, "https": None}
    )
    
    if verify_response.status_code == 200:
        company = verify_response.json()
        print(f"Company name: {company.get('name')}")
        print(f"Brand colors: {company.get('brand_colors', [])}")
    
if __name__ == "__main__":
    test_formdata_company_update()
