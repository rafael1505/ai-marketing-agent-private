#!/usr/bin/env python3
"""
Quick verification that everything is working
"""
import requests
import json

def quick_test():
    print("🔍 Quick Verification - AI Marketing Agent Image Generation")
    print("=" * 60)
    
    # Test 1: Direct API
    try:
        response = requests.get("http://127.0.0.1:8089/health", timeout=3)
        print(f"✅ API Server: {response.status_code} - {response.json()['status']}")
    except Exception as e:
        print(f"❌ API Server: {e}")
        return
    
    # Test 2: Image generation
    try:
        url = "http://127.0.0.1:8089/api/v1/ai/generate-image"
        params = {"prompt": "test", "size": "256x256", "ai_provider": "free-test-provider"}
        response = requests.post(url, params=params, timeout=5)
        data = response.json()
        
        if data.get("success") and data.get("image_url", "").startswith("data:image/svg+xml"):
            print("✅ Image Generation: Working - SVG data URLs")
        else:
            print(f"❌ Image Generation: Failed - {data}")
            return
    except Exception as e:
        print(f"❌ Image Generation: {e}")
        return
    
    # Test 3: Frontend health
    try:
        response = requests.get("http://localhost:3001", timeout=3)
        print(f"✅ Frontend: {response.status_code} - Running")
    except Exception as e:
        print(f"❌ Frontend: {e}")
        return
    
    # Test 4: Frontend proxy
    try:
        url = "http://localhost:3001/api/v1/ai/generate-image"
        params = {"prompt": "test", "size": "256x256", "ai_provider": "free-test-provider"}
        response = requests.post(url, params=params, timeout=5)
        data = response.json()
        
        if data.get("success"):
            print("✅ Frontend Proxy: Working")
        else:
            print(f"❌ Frontend Proxy: Failed - {data}")
            return
    except Exception as e:
        print(f"❌ Frontend Proxy: {e}")
        return
    
    print("\n🎉 ALL SYSTEMS WORKING!")
    print("\n📋 Test these pages in your browser:")
    print("   • Image Test Page: http://localhost:3001/image-generation-test.html")
    print("   • Create Material: http://localhost:3001/en/materials/create") 
    print("   • Edit Material: http://localhost:3001/en/materials/[id]/edit")
    print("\n💡 Images should now load as colorful SVG graphics!")

if __name__ == "__main__":
    quick_test()
