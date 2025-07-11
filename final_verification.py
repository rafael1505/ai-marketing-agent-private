#!/usr/bin/env python3
"""
Final verification script for image generation functionality
"""

import requests
import json
import time
from datetime import datetime

def test_api_endpoint():
    """Test the API endpoint directly"""
    print("🔍 Testing API endpoint...")
    
    url = "http://localhost:8089/api/v1/ai/generate-image"
    params = {
        "prompt": "modern tech product marketing image",
        "ai_provider": "free-test-provider",
        "size": "1024x1024",
        "style": "photorealistic"
    }
    
    headers = {"Content-Type": "application/json"}
    
    try:
        response = requests.post(url, params=params, headers=headers, timeout=5)
        if response.status_code == 200:
            result = response.json()
            print(f"✅ API Test: SUCCESS")
            print(f"   - Status: {response.status_code}")
            print(f"   - Image URL: {result.get('image_url')}")
            print(f"   - Provider: {result.get('provider')}")
            return True
        else:
            print(f"❌ API Test: FAILED - Status {response.status_code}")
            print(f"   - Error: {response.text}")
            return False
    except Exception as e:
        print(f"❌ API Test: EXCEPTION - {e}")
        return False

def test_multiple_requests():
    """Test multiple concurrent requests"""
    print("\n🔄 Testing multiple requests...")
    
    prompts = [
        "marketing campaign visual",
        "business presentation slide", 
        "product showcase image",
        "corporate branding design",
        "digital marketing banner"
    ]
    
    success_count = 0
    
    for i, prompt in enumerate(prompts):
        try:
            url = f"http://localhost:8089/api/v1/ai/generate-image?prompt={prompt}&ai_provider=free-test-provider"
            response = requests.post(url, headers={"Content-Type": "application/json"}, timeout=3)
            
            if response.status_code == 200:
                result = response.json()
                print(f"✅ Request {i+1}: SUCCESS - {result.get('image_url', 'No URL')}")
                success_count += 1
            else:
                print(f"❌ Request {i+1}: FAILED - {response.status_code}")
        except Exception as e:
            print(f"❌ Request {i+1}: EXCEPTION - {e}")
    
    print(f"\n📊 Multiple Requests: {success_count}/{len(prompts)} successful")
    return success_count == len(prompts)

def check_server_status():
    """Check if the server is running"""
    print("\n🏥 Checking server status...")
    
    try:
        response = requests.get("http://localhost:8089/health", timeout=3)
        if response.status_code == 200:
            print("✅ Server Health: OK")
            return True
        else:
            print(f"❌ Server Health: Status {response.status_code}")
            return False
    except Exception as e:
        print(f"❌ Server Health: EXCEPTION - {e}")
        return False

def main():
    """Run all tests"""
    print("🚀 Image Generation Final Verification")
    print("=" * 50)
    print(f"Timestamp: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
    print()
    
    tests = [
        ("Server Status", check_server_status),
        ("API Endpoint", test_api_endpoint),
        ("Multiple Requests", test_multiple_requests)
    ]
    
    results = []
    
    for test_name, test_func in tests:
        try:
            result = test_func()
            results.append((test_name, result))
        except Exception as e:
            print(f"❌ {test_name}: EXCEPTION - {e}")
            results.append((test_name, False))
    
    print("\n" + "=" * 50)
    print("🎯 FINAL RESULTS:")
    
    all_passed = True
    for test_name, result in results:
        status = "✅ PASS" if result else "❌ FAIL"
        print(f"   {test_name}: {status}")
        if not result:
            all_passed = False
    
    print("\n" + "=" * 50)
    if all_passed:
        print("🎉 ALL TESTS PASSED! Image generation is working correctly.")
    else:
        print("💥 SOME TESTS FAILED! Please check the issues above.")
    
    return all_passed

if __name__ == "__main__":
    success = main()
    exit(0 if success else 1)
