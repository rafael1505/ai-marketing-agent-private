#!/usr/bin/env python3
"""
Final comprehensive test to verify image generation is working end-to-end
"""
import requests
import json
import time

def test_api_health():
    """Test API server health"""
    try:
        response = requests.get("http://127.0.0.1:8089/health", timeout=5)
        print(f"✅ API Health: {response.status_code} - {response.json()}")
        return True
    except Exception as e:
        print(f"❌ API Health failed: {e}")
        return False

def test_image_generation():
    """Test image generation endpoint"""
    try:
        url = "http://127.0.0.1:8089/api/v1/ai/generate-image"
        params = {
            "prompt": "A beautiful marketing image for technology",
            "size": "512x512",
            "style": "photorealistic",
            "ai_provider": "free-test-provider"
        }
        
        response = requests.post(url, params=params, timeout=10)
        print(f"✅ Image Generation: {response.status_code}")
        
        if response.status_code == 200:
            data = response.json()
            if data.get("success") and data.get("image_url"):
                image_url = data["image_url"]
                print(f"   📷 Image URL length: {len(image_url)} chars")
                print(f"   📷 Format: {data.get('metadata', {}).get('format', 'unknown')}")
                print(f"   📷 Service: {data.get('metadata', {}).get('service', 'unknown')}")
                
                # Verify it's a data URL
                if image_url.startswith("data:image/svg+xml;base64,"):
                    print("   ✅ Valid SVG data URL format")
                    return True
                else:
                    print("   ❌ Invalid image URL format")
                    return False
            else:
                print(f"   ❌ Invalid response structure: {data}")
                return False
        else:
            print(f"   ❌ Failed with status {response.status_code}: {response.text}")
            return False
            
    except Exception as e:
        print(f"❌ Image Generation failed: {e}")
        return False

def test_frontend_health():
    """Test frontend is running"""
    try:
        response = requests.get("http://localhost:3001", timeout=5)
        print(f"✅ Frontend Health: {response.status_code}")
        return True
    except Exception as e:
        print(f"❌ Frontend Health failed: {e}")
        return False

def test_proxy_connection():
    """Test frontend proxy to API"""
    try:
        # Test through Next.js proxy
        url = "http://localhost:3001/api/v1/ai/generate-image"
        params = {
            "prompt": "Test proxy image",
            "size": "256x256",
            "ai_provider": "free-test-provider"
        }
        
        response = requests.post(url, params=params, timeout=10)
        print(f"✅ Frontend Proxy: {response.status_code}")
        
        if response.status_code == 200:
            data = response.json()
            if data.get("success") and data.get("image_url"):
                print("   ✅ Proxy correctly forwarding to API")
                return True
        
        print(f"   ❌ Proxy response: {response.text[:200]}")
        return False
        
    except Exception as e:
        print(f"❌ Frontend Proxy failed: {e}")
        return False

def main():
    print("🔍 Final Comprehensive Test - AI Marketing Agent Image Generation")
    print("=" * 70)
    
    # Test components
    tests = [
        ("API Server Health", test_api_health),
        ("Image Generation API", test_image_generation),
        ("Frontend Health", test_frontend_health),
        ("Frontend-to-API Proxy", test_proxy_connection),
    ]
    
    results = []
    for test_name, test_func in tests:
        print(f"\n🧪 Testing {test_name}...")
        result = test_func()
        results.append((test_name, result))
        time.sleep(1)  # Brief pause between tests
    
    # Summary
    print("\n" + "=" * 70)
    print("📊 TEST SUMMARY")
    print("=" * 70)
    
    passed = 0
    for test_name, result in results:
        status = "✅ PASS" if result else "❌ FAIL"
        print(f"{status} - {test_name}")
        if result:
            passed += 1
    
    total = len(results)
    print(f"\nOverall: {passed}/{total} tests passed")
    
    if passed == total:
        print("\n🎉 All systems are working! Image generation should be functional.")
        print("\n📋 Test these pages in your browser:")
        print("   • Image Test Page: http://localhost:3001/image-generation-test.html")
        print("   • Create Material: http://localhost:3001/en/materials/create")
        print("   • Edit Material: http://localhost:3001/en/materials/[id]/edit")
    else:
        print(f"\n⚠️  Some tests failed. Please check the failed components.")

if __name__ == "__main__":
    main()
