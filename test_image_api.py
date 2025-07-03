#!/usr/bin/env python3
"""
Test script to verify the image generation API endpoint works correctly
"""
import requests
import json

API_BASE = "http://127.0.0.1:8088/api/v1"
TOKEN = "eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9.eyJzdWIiOiJ0ZXN0QGV4YW1wbGUuY29tIiwibmFtZSI6IlRlc3QgVXNlciIsInJvbGUiOiJhZG1pbiIsImlhdCI6MTc0ODYxNjIwNiwiZXhwIjoxNzUxMjA4MjA2fQ.5tet1p59rOC6bsn7hnyr-i3O-C42IyVJ1qevxLDwfYw"

headers = {
    "Authorization": f"Bearer {TOKEN}",
    "Content-Type": "application/json"
}

def test_api_connection():
    """Test basic API connection"""
    try:
        response = requests.get(f"{API_BASE}/diagnostic/ping")
        print(f"✅ API Connection: {response.status_code}")
        return True
    except Exception as e:
        print(f"❌ API Connection failed: {e}")
        return False

def test_create_material():
    """Test creating a material"""
    try:
        data = {
            "title": "Test Material",
            "description": "Test description",
            "target_audience": "Developers",
            "campaign_objective": "Test objective",
            "keywords": ["test", "api"],
            "stage": "idea",
            "status": "draft"
        }
        
        response = requests.post(f"{API_BASE}/materials", headers=headers, json=data)
        print(f"✅ Create Material: {response.status_code}")
        
        if response.status_code == 200:
            material = response.json()
            print(f"   Material ID: {material.get('id')}")
            return material.get('id')
        else:
            print(f"   Error: {response.text}")
            return None
    except Exception as e:
        print(f"❌ Create Material failed: {e}")
        return None

def test_add_image(material_id):
    """Test adding an image to a material"""
    try:
        # Test the query parameter approach
        url = f"{API_BASE}/materials/{material_id}/images"
        params = {
            "url": "https://picsum.photos/512/512",
            "prompt": "Test image prompt",
            "ai_provider": "test_provider",
            "generation_params": json.dumps({"width": 512, "height": 512})
        }
        
        response = requests.post(url, headers=headers, params=params)
        print(f"✅ Add Image: {response.status_code}")
        
        if response.status_code != 200:
            print(f"   Error: {response.text}")
            return False
        else:
            print(f"   Image added successfully")
            return True
    except Exception as e:
        print(f"❌ Add Image failed: {e}")
        return False

def main():
    print("🧪 Testing AI Marketing Agent API endpoints...")
    print("=" * 50)
    
    # Test API connection
    if not test_api_connection():
        return
    
    # Test creating material
    material_id = test_create_material()
    if not material_id:
        return
    
    # Test adding image
    test_add_image(material_id)
    
    print("=" * 50)
    print("✅ All tests completed!")

if __name__ == "__main__":
    main()
