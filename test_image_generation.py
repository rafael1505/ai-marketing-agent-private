#!/usr/bin/env python3
"""
Test script to verify image generation API is working
"""

import requests
import json

def test_image_generation():
    """Test the image generation API endpoint"""
    url = "http://localhost:8088/api/v1/ai/generate-image"
    
    params = {
        "prompt": "modern tech product marketing image",
        "ai_provider": "free-test-provider",
        "size": "1024x1024",
        "style": "photorealistic"
    }
    
    headers = {
        "Authorization": "Bearer eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9.eyJzdWIiOiIxIiwiZW1haWwiOiJ0ZXN0QGV4YW1wbGUuY29tIiwibmFtZSI6IlRlc3QgVXNlciIsInJvbGUiOiJhZG1pbiIsImlzX2FkbWluIjp0cnVlLCJpYXQiOjE3NTE0OTY4NjUsImV4cCI6MTc1NDA4ODg2NX0.1QglhuJU3ipmB1qt74lIRvhU-xk3-UkiwFBuzVvcYWc",
        "Content-Type": "application/json"
    }
    
    print("Testing image generation API...")
    print(f"URL: {url}")
    print(f"Params: {params}")
    
    try:
        response = requests.post(url, params=params, headers=headers)
        print(f"Status Code: {response.status_code}")
        
        if response.status_code == 200:
            result = response.json()
            print("✅ SUCCESS!")
            print(f"Image URL: {result.get('image_url')}")
            print(f"Provider: {result.get('provider')}")
            print(f"Success: {result.get('success')}")
            return True
        else:
            print("❌ FAILED!")
            print(f"Error: {response.text}")
            return False
            
    except Exception as e:
        print(f"❌ Exception: {e}")
        return False

if __name__ == "__main__":
    success = test_image_generation()
    if success:
        print("\n🎉 Image generation API is working correctly!")
    else:
        print("\n💥 Image generation API has issues!")
