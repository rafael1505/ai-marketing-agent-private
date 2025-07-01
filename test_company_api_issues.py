#!/usr/bin/env python3
"""
Test script to identify and fix company API issues
"""
import requests
import json
import time
import sys

API_BASE_URL = "http://127.0.0.1:8088/api/v1"
FRONTEND_URL = "http://127.0.0.1:3001"

def test_api_server():
    """Test if API server is running"""
    print("=== Testing API Server ===")
    try:
        response = requests.get(f"{API_BASE_URL}/diagnostic/health", timeout=5)
        print(f"✅ API server is running (status: {response.status_code})")
        return True
    except requests.exceptions.ConnectionError:
        print("❌ API server is not running")
        return False
    except Exception as e:
        print(f"❌ API server test failed: {e}")
        return False

def get_test_token():
    """Get authentication token for testing"""
    print("\n=== Getting Authentication Token ===")
    
    # Try to get existing token
    try:
        login_data = {
            "username": "test@example.com", 
            "password": "password"
        }
        
        response = requests.post(f"{API_BASE_URL}/auth/login", data=login_data)
        if response.status_code == 200:
            token_data = response.json()
            token = token_data.get('access_token')
            print(f"✅ Got authentication token: {token[:20]}...")
            return token
        else:
            print(f"❌ Login failed: {response.status_code} - {response.text}")
            
    except Exception as e:
        print(f"❌ Login error: {e}")
    
    # Fallback to development token
    print("🔄 Using development token...")
    return "DEVELOPMENT_MOCK_TOKEN_FOR_TESTING"

def test_company_get():
    """Test getting company information"""
    print("\n=== Testing Company GET ===")
    try:
        response = requests.get(f"{API_BASE_URL}/companies/active", timeout=10)
        print(f"Status: {response.status_code}")
        
        if response.status_code == 200:
            data = response.json()
            print(f"✅ GET company successful")
            print(f"Company: {data.get('name', 'Unknown')}")
            print(f"Colors: {data.get('brand_colors', [])}")
            return data
        else:
            print(f"❌ GET company failed: {response.text}")
            return None
            
    except Exception as e:
        print(f"❌ GET company error: {e}")
        return None

def test_company_update_json(token):
    """Test updating company with JSON data"""
    print("\n=== Testing Company UPDATE (JSON) ===")
    
    headers = {"Authorization": f"Bearer {token}", "Content-Type": "application/json"}
    data = {
        "name": "Test Company JSON Update",
        "description": "Updated via JSON",
        "brand_colors": ["#FF5733", "#33FF57"]
    }
    
    try:
        response = requests.put(
            f"{API_BASE_URL}/companies/test_company", 
            headers=headers,
            json=data,
            timeout=15
        )
        
        print(f"Status: {response.status_code}")
        print(f"Response: {response.text}")
        
        if response.status_code == 200:
            print("✅ JSON update successful")
            return True
        else:
            print(f"❌ JSON update failed")
            return False
            
    except Exception as e:
        print(f"❌ JSON update error: {e}")
        return False

def test_company_update_formdata(token):
    """Test updating company with FormData"""
    print("\n=== Testing Company UPDATE (FormData) ===")
    
    headers = {"Authorization": f"Bearer {token}"}
    
    # Create FormData
    data = {
        "name": "Test Company FormData Update",
        "description": "Updated via FormData",
        "brand_colors[0]": "#FF5733",
        "brand_colors[1]": "#33FF57"
    }
    
    # Create a test file
    files = {
        'logo_file': ('test_logo.txt', b'test logo content', 'text/plain')
    }
    
    try:
        response = requests.put(
            f"{API_BASE_URL}/companies/test_company",
            headers=headers,
            data=data,
            files=files,
            timeout=15
        )
        
        print(f"Status: {response.status_code}")
        print(f"Response: {response.text}")
        
        if response.status_code == 200:
            print("✅ FormData update successful")
            return True
        else:
            print(f"❌ FormData update failed")
            return False
            
    except Exception as e:
        print(f"❌ FormData update error: {e}")
        return False

def test_brand_colors_issue():
    """Test specific brand_colors array handling issue"""
    print("\n=== Testing Brand Colors Array Issue ===")
    
    token = get_test_token()
    if not token:
        print("❌ Cannot test without token")
        return False
    
    # Test different ways of sending brand_colors
    test_cases = [
        {
            "name": "JSON Array",
            "data": {"brand_colors": ["#FF0000", "#00FF00"]},
            "method": "json"
        },
        {
            "name": "FormData indexed",
            "data": {"brand_colors[0]": "#FF0000", "brand_colors[1]": "#00FF00"},
            "method": "formdata"
        },
        {
            "name": "FormData repeated",
            "data": [("brand_colors", "#FF0000"), ("brand_colors", "#00FF00")],
            "method": "formdata_repeated"
        }
    ]
    
    for test_case in test_cases:
        print(f"\n--- Testing {test_case['name']} ---")
        headers = {"Authorization": f"Bearer {token}"}
        
        try:
            if test_case["method"] == "json":
                headers["Content-Type"] = "application/json"
                response = requests.put(
                    f"{API_BASE_URL}/companies/test_company",
                    headers=headers,
                    json=test_case["data"],
                    timeout=10
                )
            elif test_case["method"] == "formdata":
                response = requests.put(
                    f"{API_BASE_URL}/companies/test_company",
                    headers=headers,
                    data=test_case["data"],
                    timeout=10
                )
            elif test_case["method"] == "formdata_repeated":
                # Use files parameter to send repeated form fields
                response = requests.put(
                    f"{API_BASE_URL}/companies/test_company",
                    headers=headers,
                    files=test_case["data"],
                    timeout=10
                )
            
            print(f"Status: {response.status_code}")
            if response.status_code == 200:
                result = response.json()
                colors = result.get("brand_colors", [])
                print(f"✅ Success - Colors: {colors}")
            else:
                print(f"❌ Failed: {response.text}")
                
        except Exception as e:
            print(f"❌ Error: {e}")

def main():
    print("🔍 Company API Issues Diagnostic Tool")
    print("=" * 50)
    
    # Check if API server is running
    if not test_api_server():
        print("\n❌ API server must be running to continue")
        print("Please start the API server with:")
        print("uvicorn app.main:app --host 127.0.0.1 --port 8088 --reload")
        sys.exit(1)
    
    # Test basic company operations
    company_data = test_company_get()
    
    # Get authentication token
    token = get_test_token()
    if not token:
        print("❌ Cannot proceed without authentication token")
        sys.exit(1)
    
    # Test different update methods
    json_result = test_company_update_json(token)
    formdata_result = test_company_update_formdata(token)
    
    # Test specific brand_colors issue
    test_brand_colors_issue()
    
    # Summary
    print("\n" + "=" * 50)
    print("📊 SUMMARY")
    print("=" * 50)
    print(f"GET company: {'✅ Working' if company_data else '❌ Failed'}")
    print(f"JSON update: {'✅ Working' if json_result else '❌ Failed'}")
    print(f"FormData update: {'✅ Working' if formdata_result else '❌ Failed'}")
    
    if not formdata_result:
        print("\n🔧 LIKELY ISSUES:")
        print("1. FormData authentication not working properly")
        print("2. Brand colors array not being parsed correctly")
        print("3. File upload handling issues")
        print("4. Database persistence problems")

if __name__ == "__main__":
    main()
