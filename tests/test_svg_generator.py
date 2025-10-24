#!/usr/bin/env python3
"""
Quick test for the new SVG image generator
"""

import requests
import json

def test_svg_generation():
    """Test that SVG images are generated correctly"""
    print("🎨 Testing SVG Image Generation...")
    
    url = "http://localhost:8089/api/v1/ai/generate-image"
    params = {
        "prompt": "marketing banner design",
        "ai_provider": "free-test-provider",
        "size": "1024x1024"
    }
    
    try:
        response = requests.post(url, params=params, headers={"Content-Type": "application/json"}, timeout=5)
        
        if response.status_code == 200:
            result = response.json()
            image_url = result.get('image_url', '')
            
            print(f"✅ Status: {response.status_code}")
            print(f"✅ Success: {result.get('success')}")
            print(f"✅ Provider: {result.get('provider')}")
            print(f"✅ Service: {result.get('metadata', {}).get('service')}")
            
            if image_url.startswith('data:image/svg+xml;base64,'):
                print("✅ Image Format: SVG Data URL (correct)")
                print(f"✅ Image URL Length: {len(image_url)} characters")
                return True
            else:
                print(f"❌ Unexpected image format: {image_url[:100]}...")
                return False
        else:
            print(f"❌ HTTP Error: {response.status_code}")
            print(f"❌ Response: {response.text}")
            return False
            
    except Exception as e:
        print(f"❌ Exception: {e}")
        return False

if __name__ == "__main__":
    success = test_svg_generation()
    if success:
        print("\n🎉 SVG image generation is working correctly!")
    else:
        print("\n💥 SVG image generation has issues!")
    
    print("\n📝 You can now test the frontend pages:")
    print("   - Test Page: http://localhost:3001/image-generation-test.html")
    print("   - Create Material: http://localhost:3001/en/materials/create") 
    print("   - Edit Material: http://localhost:3001/en/materials/1/edit")
