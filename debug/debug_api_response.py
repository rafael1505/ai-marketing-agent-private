#!/usr/bin/env python3

"""
Simplified test script to diagnose API response issues
"""

import requests
import json
import os

def test_api_response():
    base_url = "http://127.0.0.1:8088"
    endpoint = "/api/v1/companies/active"
    mock_token = "DEVELOPMENT_MOCK_TOKEN_FOR_TESTING"
    
    print(f"\n🔍 TESTING API RESPONSE FOR {endpoint}\n" + "="*40)
    
    # Make request
    print("Sending GET request...")
    # Ensure we completely bypass any proxies
    old_http_proxy = os.environ.pop('http_proxy', None)
    old_https_proxy = os.environ.pop('https_proxy', None)
    old_no_proxy = os.environ.pop('no_proxy', None)
    
    try:
        response = requests.get(
            f"{base_url}{endpoint}", 
            headers={"Authorization": f"Bearer {mock_token}"},
            proxies={"http": None, "https": None},
            timeout=5
        )
        
        print(f"Status Code: {response.status_code}")
        print(f"Headers: {dict(response.headers)}")
        
        # Print raw response
        print("\nRaw Response:")
        print("-" * 40)
        print(response.text)
        print("-" * 40)
        
        # Try to parse as JSON
        print("\nTrying to parse as JSON:")
        try:
            data = response.json()
            print("✅ Successfully parsed as JSON")
            print(f"JSON data: {json.dumps(data, indent=2)}")
        except json.JSONDecodeError as e:
            print(f"❌ JSON parsing failed: {e}")
            
    except Exception as e:
        print(f"❌ Request failed: {str(e)}")
    finally:
        # Restore environment variables
        if old_http_proxy:
            os.environ['http_proxy'] = old_http_proxy
        if old_https_proxy:
            os.environ['https_proxy'] = old_https_proxy
        if old_no_proxy:
            os.environ['no_proxy'] = old_no_proxy

if __name__ == "__main__":
    test_api_response()
