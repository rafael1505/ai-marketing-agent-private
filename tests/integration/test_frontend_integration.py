#!/usr/bin/env python3
"""
Test the full AI provider integration with the frontend
"""
import requests
import json

def test_frontend_integration():
    """Test if the frontend can access the AI provider endpoints"""
    print("🧪 Testing Frontend AI Provider Integration")
    print("=" * 60)
    
    # Test main API endpoints
    base_url = "http://127.0.0.1:8088"
    
    # Test 1: Health check
    print("\n1️⃣ Testing API health...")
    try:
        response = requests.get(f"{base_url}/health", timeout=5)
        if response.status_code == 200:
            print("✅ API is healthy")
        else:
            print(f"❌ API health check failed: {response.status_code}")
    except Exception as e:
        print(f"❌ API health check error: {e}")
    
    # Test 2: AI providers endpoint
    print("\n2️⃣ Testing AI providers endpoint...")
    try:
        response = requests.get(f"{base_url}/api/v1/ai/providers", timeout=10)
        if response.status_code == 200:
            data = response.json()
            providers = data.get('providers', [])
            print(f"✅ Found {len(providers)} AI providers")
            for provider in providers:
                status = "✅ Available" if provider.get('available') else "❌ Unavailable"
                print(f"   - {provider.get('name', 'Unknown')}: {status}")
        else:
            print(f"❌ Providers endpoint failed: {response.status_code}")
            print(f"   Response: {response.text[:200]}")
    except Exception as e:
        print(f"❌ Providers endpoint error: {e}")
    
    # Test 3: Image generation endpoint
    print("\n3️⃣ Testing image generation...")
    try:
        test_request = {
            "prompt": "A test image for frontend integration",
            "provider": "free-test-provider",
            "size": "512x512",
            "variations": 2
        }
        
        response = requests.post(
            f"{base_url}/api/v1/ai/generate-image",
            json=test_request,
            timeout=30
        )
        
        if response.status_code == 200:
            data = response.json()
            if data.get('success'):
                images = data.get('images', [])
                print(f"✅ Generated {len(images)} images successfully")
                print(f"   Provider: {data.get('provider')}")
                print(f"   Model: {data.get('model')}")
                cost = data.get('cost', 0)
                if cost > 0:
                    print(f"   Cost: ${cost:.4f}")
                else:
                    print("   Cost: Free")
            else:
                print(f"❌ Generation failed: {data.get('error', 'Unknown error')}")
        else:
            print(f"❌ Generation endpoint failed: {response.status_code}")
            print(f"   Response: {response.text[:200]}")
    except Exception as e:
        print(f"❌ Generation endpoint error: {e}")
    
    # Test 4: Frontend accessibility
    print("\n4️⃣ Testing frontend accessibility...")
    try:
        response = requests.get("http://localhost:3001", timeout=5)
        if response.status_code == 200:
            print("✅ Frontend is accessible")
        else:
            print(f"❌ Frontend not accessible: {response.status_code}")
    except Exception as e:
        print(f"❌ Frontend accessibility error: {e}")
    
    # Test 5: Test server fallback
    print("\n5️⃣ Testing fallback server...")
    try:
        response = requests.get("http://127.0.0.1:8089/providers", timeout=5)
        if response.status_code == 200:
            data = response.json()
            providers = data.get('providers', [])
            print(f"✅ Fallback server working with {len(providers)} providers")
        else:
            print(f"❌ Fallback server failed: {response.status_code}")
    except Exception as e:
        print(f"❌ Fallback server error: {e}")
    
    print("\n🎉 Integration test complete!")
    print("\n📋 Summary:")
    print("- Main API: http://127.0.0.1:8088")
    print("- Frontend: http://localhost:3001")
    print("- AI Providers Page: http://localhost:3001/en/ai-providers")
    print("- Materials Creation: http://localhost:3001/en/materials/create")
    print("- Test Server: http://127.0.0.1:8089")

if __name__ == "__main__":
    test_frontend_integration()
