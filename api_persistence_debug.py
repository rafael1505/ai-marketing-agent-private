#!/usr/bin/env python3
"""
API Debug Tool for Company Persistence
This script tests the API endpoints with verbose logging
"""
import requests
import json
import uuid
import time

# Configuration
BASE_URL = "http://127.0.0.1:8088" 
AUTH_TOKEN = "DEVELOPMENT_MOCK_TOKEN_FOR_TESTING"
AUTH_HEADERS = {"Authorization": f"Bearer {AUTH_TOKEN}"}

def print_response(response):
    """Pretty print API response"""
    print(f"Status: {response.status_code}")
    print(f"Headers: {json.dumps(dict(response.headers), indent=2)}")
    try:
        print(f"Body: {json.dumps(response.json(), indent=2)}")
    except:
        print(f"Body: {response.text[:200]}")
    print("-" * 50)

def test_api_health():
    """Verify API is running"""
    print("\n=== Testing API Health ===")
    try:
        response = requests.get(f"{BASE_URL}/api/v1/diagnostic/health")
        print_response(response)
        return response.status_code == 200
    except Exception as e:
        print(f"Error: {e}")
        return False

def get_active_company():
    """Get active company with full details"""
    print("\n=== Getting Active Company ===")
    try:
        response = requests.get(
            f"{BASE_URL}/api/v1/companies/active",
            headers=AUTH_HEADERS
        )
        print_response(response)
        return response.json() if response.status_code == 200 else None
    except Exception as e:
        print(f"Error: {e}")
        return None

def update_company_form_data(company_id, name, colors):
    """Update company using FormData format"""
    print("\n=== Updating Company (FormData) ===")
    
    data = {
        "name": name,
        "description": "Updated with FormData"
    }
    
    # Add colors with array indexing
    for i, color in enumerate(colors):
        data[f"brand_colors[{i}]"] = color
    
    print(f"Request data: {json.dumps(data, indent=2)}")
    
    try:
        response = requests.put(
            f"{BASE_URL}/api/v1/companies/{company_id}",
            data=data,
            headers=AUTH_HEADERS
        )
        print_response(response)
        return response.json() if response.status_code == 200 else None
    except Exception as e:
        print(f"Error: {e}")
        return None

def update_company_json(company_id, name, colors):
    """Update company using JSON format"""
    print("\n=== Updating Company (JSON) ===")
    
    data = {
        "name": name,
        "description": "Updated with JSON",
        "brand_colors": colors
    }
    
    print(f"Request data: {json.dumps(data, indent=2)}")
    
    try:
        headers = {**AUTH_HEADERS, "Content-Type": "application/json"}
        response = requests.put(
            f"{BASE_URL}/api/v1/companies/{company_id}",
            json=data,
            headers=headers
        )
        print_response(response)
        return response.json() if response.status_code == 200 else None
    except Exception as e:
        print(f"Error: {e}")
        return None

def main():
    print("=== Company API Debug Tool ===")
    
    # Check API health
    if not test_api_health():
        print("❌ API is not responding. Exiting.")
        return
    
    # Get company
    company = get_active_company()
    if not company:
        print("❌ Could not get company. Exiting.")
        return
    
    company_id = company.get("id")
    print(f"Working with company ID: {company_id}")
    
    # Generate unique test values
    test_id = uuid.uuid4().hex[:8]
    form_colors = [f"#FORM{test_id}1", f"#FORM{test_id}2"]
    json_colors = [f"#JSON{test_id}1", f"#JSON{test_id}2"]
    
    # Update with FormData
    form_name = f"FormData Test {test_id}"
    print(f"\nUpdating with FormData: {form_name}, colors: {form_colors}")
    form_result = update_company_form_data(company_id, form_name, form_colors)
    
    # Check persistence
    print("\n=== Checking FormData Update Persistence ===")
    time.sleep(1)
    company_after_form = get_active_company()
    
    if company_after_form:
        name_match = company_after_form.get("name") == form_name
        colors_match = sorted(company_after_form.get("brand_colors", [])) == sorted(form_colors)
        
        if name_match and colors_match:
            print("✅ FormData update persisted successfully!")
        elif name_match:
            print("⚠️ Name persisted but colors did not!")
            print(f"Expected colors: {form_colors}")
            print(f"Actual colors: {company_after_form.get('brand_colors', [])}")
        elif colors_match:
            print("⚠️ Colors persisted but name did not!")
            print(f"Expected name: {form_name}")
            print(f"Actual name: {company_after_form.get('name')}")
        else:
            print("❌ Neither name nor colors persisted!")
    
    # Update with JSON
    json_name = f"JSON Test {test_id}"
    print(f"\nUpdating with JSON: {json_name}, colors: {json_colors}")
    json_result = update_company_json(company_id, json_name, json_colors)
    
    # Check persistence
    print("\n=== Checking JSON Update Persistence ===")
    time.sleep(1)
    company_after_json = get_active_company()
    
    if company_after_json:
        name_match = company_after_json.get("name") == json_name
        colors_match = sorted(company_after_json.get("brand_colors", [])) == sorted(json_colors)
        
        if name_match and colors_match:
            print("✅ JSON update persisted successfully!")
        elif name_match:
            print("⚠️ Name persisted but colors did not!")
            print(f"Expected colors: {json_colors}")
            print(f"Actual colors: {company_after_json.get('brand_colors', [])}")
        elif colors_match:
            print("⚠️ Colors persisted but name did not!")
            print(f"Expected name: {json_name}")
            print(f"Actual name: {company_after_json.get('name')}")
        else:
            print("❌ Neither name nor colors persisted!")
    
if __name__ == "__main__":
    main()
