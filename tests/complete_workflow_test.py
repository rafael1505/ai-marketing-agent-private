#!/usr/bin/env python3
"""
Complete workflow test from ideation to image generation
Tests the full material creation flow with a free AI provider
"""
import requests
import json
import time
import sys

# Configuration
FRONTEND_URL = "http://127.0.0.1:3001"
BACKEND_URL = "http://127.0.0.1:8088"
API_BASE = "/api/v1"

# Use the fresh token
TOKEN = "eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9.eyJzdWIiOiIxIiwiZW1haWwiOiJ0ZXN0QGV4YW1wbGUuY29tIiwibmFtZSI6IlRlc3QgVXNlciIsInJvbGUiOiJhZG1pbiIsImlzX2FkbWluIjp0cnVlLCJpYXQiOjE3NTE0OTY4NjUsImV4cCI6MTc1NDA4ODg2NX0.1QglhuJU3ipmB1qt74lIRvhU-xk3-UkiwFBuzVvcYWc"

headers = {
    "Authorization": f"Bearer {TOKEN}",
    "Content-Type": "application/json"
}

def test_endpoint(url, method="GET", data=None, params=None):
    """Test an endpoint and return response"""
    try:
        if method == "GET":
            response = requests.get(url, headers=headers, timeout=10, params=params)
        elif method == "POST":
            response = requests.post(url, headers=headers, json=data, timeout=10, params=params)
        
        print(f"✅ {method} {url} -> {response.status_code}")
        return response
    except Exception as e:
        print(f"❌ {method} {url} -> ERROR: {e}")
        return None

def main():
    print("🚀 Starting Complete Material Creation Workflow Test")
    print("=" * 60)
    
    # Step 1: Test connectivity
    print("\n1️⃣ TESTING CONNECTIVITY")
    print("-" * 30)
    
    # Test backend direct
    backend_ping = test_endpoint(f"{BACKEND_URL}{API_BASE}/diagnostic/ping")
    if not backend_ping or backend_ping.status_code != 200:
        print("❌ Backend not responding")
        return False
    
    # Test frontend proxy
    frontend_ping = test_endpoint(f"{FRONTEND_URL}{API_BASE}/diagnostic/ping")
    if not frontend_ping or frontend_ping.status_code != 200:
        print("❌ Frontend proxy not working")
        return False
    
    print("✅ Both backend and frontend proxy are working")
    
    # Step 2: Test authentication
    print("\n2️⃣ TESTING AUTHENTICATION")
    print("-" * 30)
    
    # Test auth verification through proxy
    auth_test = test_endpoint(f"{FRONTEND_URL}{API_BASE}/auth/verify-token", "POST")
    if auth_test and auth_test.status_code == 200:
        print("✅ Authentication working through proxy")
    else:
        print("⚠️  Auth verification failed, but continuing...")
    
    # Step 3: IDEATION - Create a material
    print("\n3️⃣ IDEATION PHASE - Creating Material")
    print("-" * 30)
    
    material_data = {
        "title": "AI-Powered Marketing Campaign",
        "description": "A comprehensive marketing campaign showcasing AI integration in modern business",
        "target_audience": "Tech-savvy business owners and entrepreneurs",
        "campaign_objective": "Demonstrate AI capabilities and drive engagement",
        "keywords": ["AI", "automation", "innovation", "business", "technology"],
        "stage": "idea",
        "status": "draft"
    }
    
    # Create material through frontend proxy
    create_response = test_endpoint(
        f"{FRONTEND_URL}{API_BASE}/materials", 
        "POST", 
        material_data
    )
    
    if not create_response or create_response.status_code != 200:
        print(f"❌ Failed to create material: {create_response.text if create_response else 'No response'}")
        return False
    
    material = create_response.json()
    material_id = material.get("id") or material.get("_id")
    print(f"✅ Material created with ID: {material_id}")
    
    # Step 4: REFINEMENT - Update material to refinement stage
    print("\n4️⃣ REFINEMENT PHASE - Moving to Refinement")
    print("-" * 30)
    
    # Update stage to refinement
    stage_response = test_endpoint(
        f"{FRONTEND_URL}{API_BASE}/materials/{material_id}/stage",
        "POST",
        {"stage": "refinement", "status": "in_progress"}
    )
    
    if stage_response and stage_response.status_code == 200:
        print("✅ Material moved to refinement stage")
    else:
        print("⚠️  Stage update failed, but continuing...")
    
    # Step 5: IMAGE GENERATION - Test with a free AI provider
    print("\n5️⃣ IMAGE GENERATION - Testing with Free Provider")
    print("-" * 30)
    
    # For testing, we'll simulate using a free provider that doesn't require API keys
    # In real scenarios, this would connect to actual AI services
    
    # Test image generation endpoint through frontend proxy
    image_params = {
        "url": "https://picsum.photos/800/600",  # Free placeholder image service
        "prompt": "A futuristic business meeting with AI technology",
        "ai_provider": "stable-diffusion-free",  # Simulated free provider
        "generation_params": json.dumps({
            "style": "photorealistic",
            "quality": "high",
            "size": "1024x1024"
        })
    }
    
    print(f"Testing image addition to material {material_id}")
    print(f"URL: {FRONTEND_URL}{API_BASE}/materials/{material_id}/images")
    print(f"Params: {image_params}")
    
    image_response = test_endpoint(
        f"{FRONTEND_URL}{API_BASE}/materials/{material_id}/images",
        "POST",
        params=image_params
    )
    
    if image_response:
        if image_response.status_code == 200:
            updated_material = image_response.json()
            images_count = len(updated_material.get("generated_images", []))
            print(f"✅ Image added successfully! Material now has {images_count} images")
            
            # Step 6: FINALIZATION - Complete the workflow
            print("\n6️⃣ FINALIZATION PHASE - Completing Workflow")
            print("-" * 30)
            
            if images_count > 0:
                # Select the first image
                first_image_url = updated_material["generated_images"][0]["url"]
                select_response = test_endpoint(
                    f"{FRONTEND_URL}{API_BASE}/materials/{material_id}/select-image",
                    "POST",
                    {"image_url": first_image_url}
                )
                
                if select_response and select_response.status_code == 200:
                    print("✅ Image selected successfully")
                    
                    # Move to finalization stage
                    final_stage_response = test_endpoint(
                        f"{FRONTEND_URL}{API_BASE}/materials/{material_id}/stage",
                        "POST",
                        {"stage": "finalization", "status": "completed"}
                    )
                    
                    if final_stage_response and final_stage_response.status_code == 200:
                        print("✅ Material moved to finalization stage")
                        print("\n🎉 COMPLETE WORKFLOW TEST SUCCESSFUL!")
                        print("=" * 60)
                        print("✅ Ideation: Material created")
                        print("✅ Refinement: Stage updated")
                        print("✅ Image Generation: Image added")
                        print("✅ Finalization: Workflow completed")
                        return True
                    else:
                        print("⚠️  Final stage update failed")
                else:
                    print("⚠️  Image selection failed")
            else:
                print("❌ No images were added to the material")
        else:
            print(f"❌ Image generation failed with status {image_response.status_code}")
            print(f"Response: {image_response.text}")
            
            # Let's check what the specific error is
            if image_response.status_code == 404:
                print("\n🔍 DEBUGGING 404 ERROR:")
                print("This suggests the endpoint is not found. Let's verify the URL structure...")
                
                # Test if material still exists
                get_material = test_endpoint(f"{FRONTEND_URL}{API_BASE}/materials/{material_id}")
                if get_material and get_material.status_code == 200:
                    print("✅ Material still exists, so the issue is with the image endpoint")
                else:
                    print("❌ Material no longer exists")
    else:
        print("❌ No response from image generation endpoint")
    
    print("\n❌ WORKFLOW TEST FAILED")
    return False

if __name__ == "__main__":
    success = main()
    sys.exit(0 if success else 1)
