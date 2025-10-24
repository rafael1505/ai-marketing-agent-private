#!/usr/bin/env python3
"""
Comprehensive test with enhanced debugging
"""
import requests
import json
import time

# Configuration
FRONTEND_URL = "http://127.0.0.1:3001"
BACKEND_URL = "http://127.0.0.1:8088"
API_BASE = "/api/v1"
TOKEN = "eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9.eyJzdWIiOiIxIiwiZW1haWwiOiJ0ZXN0QGV4YW1wbGUuY29tIiwibmFtZSI6IlRlc3QgVXNlciIsInJvbGUiOiJhZG1pbiIsImlzX2FkbWluIjp0cnVlLCJpYXQiOjE3NTE0OTY4NjUsImV4cCI6MTc1NDA4ODg2NX0.1QglhuJU3ipmB1qt74lIRvhU-xk3-UkiwFBuzVvcYWc"

headers = {
    "Authorization": f"Bearer {TOKEN}",
    "Content-Type": "application/json"
}

def test_detailed():
    print("🔍 DETAILED IMAGE GENERATION TEST")
    print("=" * 50)
    
    # Step 1: Create a simple material
    print("\n1. Creating a material...")
    material_data = {
        "title": "Test Material for Image Gen",
        "description": "Testing image generation",
        "target_audience": "Developers", 
        "campaign_objective": "Test AI integration",
        "keywords": ["test"],
        "stage": "refinement",
        "status": "in_progress"
    }
    
    response = requests.post(f"{FRONTEND_URL}{API_BASE}/materials", headers=headers, json=material_data)
    print(f"Create material: {response.status_code}")
    if response.status_code != 200:
        print(f"Error: {response.text}")
        return
    
    material = response.json()
    material_id = material.get("id") or material.get("_id")
    print(f"Material created: {material_id}")
    print(f"Material company_id: {material.get('company_id')}")
    
    # Step 2: Test image addition with detailed params
    print(f"\n2. Adding image to material {material_id}...")
    
    # Test through backend directly first
    print("Testing through backend directly...")
    backend_url = f"{BACKEND_URL}{API_BASE}/materials/{material_id}/images"
    params = {
        "url": "https://picsum.photos/800/600",
        "prompt": "Test image generation",
        "ai_provider": "test-provider",
        "generation_params": json.dumps({"test": True})
    }
    
    print(f"URL: {backend_url}")
    print(f"Params: {params}")
    
    response = requests.post(backend_url, headers=headers, params=params)
    print(f"Backend response: {response.status_code}")
    if response.status_code == 200:
        result = response.json()
        images_count = len(result.get("generated_images", []))
        print(f"✅ Backend success! Images count: {images_count}")
        if images_count > 0:
            print("Generated images:")
            for i, img in enumerate(result.get("generated_images", [])):
                print(f"  {i+1}. URL: {img.get('url')}")
                print(f"     Prompt: {img.get('prompt')}")
                print(f"     Provider: {img.get('ai_provider')}")
        else:
            print("❌ No images in response")
    else:
        print(f"❌ Backend error: {response.text}")
        return
    
    # Test through frontend proxy
    print("\nTesting through frontend proxy...")
    frontend_url = f"{FRONTEND_URL}{API_BASE}/materials/{material_id}/images"
    response = requests.post(frontend_url, headers=headers, params=params)
    print(f"Frontend proxy response: {response.status_code}")
    if response.status_code == 200:
        result = response.json()
        images_count = len(result.get("generated_images", []))
        print(f"✅ Frontend proxy success! Images count: {images_count}")
    else:
        print(f"❌ Frontend proxy error: {response.text}")
    
    # Step 3: Verify the material has images
    print(f"\n3. Verifying material {material_id}...")
    response = requests.get(f"{FRONTEND_URL}{API_BASE}/materials/{material_id}", headers=headers)
    if response.status_code == 200:
        material = response.json()
        images_count = len(material.get("generated_images", []))
        print(f"✅ Material verification: {images_count} images found")
        if images_count > 0:
            print("🎉 SUCCESS: Images are properly stored!")
            return True
    else:
        print(f"❌ Material verification failed: {response.text}")
    
    return False

if __name__ == "__main__":
    test_detailed()
