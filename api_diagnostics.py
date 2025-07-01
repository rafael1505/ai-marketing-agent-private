#!/usr/bin/env python3

"""
API Diagnostic Script
This script tests the API server's health and responsiveness.
"""

import requests
import sys
import json

def test_api_health():
    print("\n🔍 API DIAGNOSTICS\n" + "="*30)
    
    base_url = "http://127.0.0.1:8088"
    
    # 1. Simple health check
    print("\n1. Testing API health endpoint...")
    try:
        response = requests.get(
            f"{base_url}/api/v1/diagnostic/health",
            proxies={"http": None, "https": None},
            timeout=3
        )
        print(f"  Status: {response.status_code}")
        if response.status_code == 200:
            print(f"  Response: {response.text[:100]}")
            print("  ✅ Health check successful")
        else:
            print(f"  ❌ Health check failed: {response.text}")
    except requests.exceptions.Timeout:
        print("  ❌ Request timed out - API server might be hanging")
    except requests.exceptions.ConnectionError:
        print("  ❌ Connection failed - API server might not be running")
    except Exception as e:
        print(f"  ❌ Error: {str(e)}")
    
    # 2. Test companies endpoint without auth
    print("\n2. Testing companies endpoint without auth...")
    try:
        response = requests.get(
            f"{base_url}/api/v1/companies/active",
            proxies={"http": None, "https": None},
            timeout=3
        )
        print(f"  Status: {response.status_code}")
        if response.status_code == 200:
            print(f"  Response: {json.dumps(response.json(), indent=2)[:100]}...")
            print("  ✅ Companies endpoint working without auth")
        elif response.status_code == 401:
            print("  ℹ️ Authentication required (expected)")
        else:
            print(f"  ❌ Unexpected status: {response.text}")
    except requests.exceptions.Timeout:
        print("  ❌ Request timed out - API server might be hanging")
    except Exception as e:
        print(f"  ❌ Error: {str(e)}")
    
    # 3. Test companies endpoint with mock auth
    print("\n3. Testing companies endpoint with mock auth...")
    try:
        response = requests.get(
            f"{base_url}/api/v1/companies/active",
            headers={"Authorization": "Bearer DEVELOPMENT_MOCK_TOKEN_FOR_TESTING"},
            proxies={"http": None, "https": None},
            timeout=3
        )
        print(f"  Status: {response.status_code}")
        if response.status_code == 200:
            print(f"  Response: {json.dumps(response.json(), indent=2)[:100]}...")
            print("  ✅ Companies endpoint working with mock auth")
        else:
            print(f"  ❌ Failed with mock auth: {response.text}")
    except requests.exceptions.Timeout:
        print("  ❌ Request timed out - API server might be hanging")
    except Exception as e:
        print(f"  ❌ Error: {str(e)}")
        
    print("\n" + "="*30)

if __name__ == "__main__":
    test_api_health()
