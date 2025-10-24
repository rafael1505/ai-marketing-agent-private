#!/usr/bin/env python3
"""
Simple API connectivity test
"""

import requests
import json

API_BASE_URL = "http://127.0.0.1:8088"
AUTH_HEADER = {"Authorization": "Bearer DEVELOPMENT_MOCK_TOKEN_FOR_TESTING"}

def test_api_connectivity():
    print("=== TESTING API CONNECTIVITY ===\n")
    
    # Try to get company list or active company
    try:
        response = requests.get(
            f"{API_BASE_URL}/api/v1/companies/active",
            headers=AUTH_HEADER,
            proxies={"http": None, "https": None}
        )
        
        print(f"Status code: {response.status_code}")
        
        if response.status_code == 200:
            data = response.json()
            print("✅ API is responding!")
            print(f"Company name: {data.get('name')}")
            print(f"Brand colors: {data.get('brand_colors')}")
            return True
        else:
            print(f"❌ API returned error: {response.status_code}")
            print(response.text)
            return False
    except Exception as e:
        print(f"❌ Failed to connect to API: {e}")
        return False

if __name__ == "__main__":
    test_api_connectivity()
