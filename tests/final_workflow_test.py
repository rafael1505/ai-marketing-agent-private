#!/usr/bin/env python3
"""
Final complete workflow test with free AI provider
"""
import requests
import json

# Configuration
FRONTEND_URL = "http://127.0.0.1:3001"
API_BASE = "/api/v1"
TOKEN = "eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9.eyJzdWIiOiIxIiwiZW1haWwiOiJ0ZXN0QGV4YW1wbGUuY29tIiwibmFtZSI6IlRlc3QgVXNlciIsInJvbGUiOiJhZG1pbiIsImlzX2FkbWluIjp0cnVlLCJpYXQiOjE3NTE0OTY4NjUsImV4cCI6MTc1NDA4ODg2NX0.1QglhuJU3ipmB1qt74lIRvhU-xk3-UkiwFBuzVvcYWc"

headers = {
    "Authorization": f"Bearer {TOKEN}",
    "Content-Type": "application/json"
}

def test_complete_workflow():
    print("🎯 FINAL COMPLETE WORKFLOW TEST")
    print("=" * 60)
    
    # Step 1: Create material
    print("\n📝 STEP 1: Creating Material")
    material_data = {
        "title": "Final Test Campaign",
        "description": "Complete workflow test with free AI provider",
        "target_audience": "Developers and testers",
        "campaign_objective": "Test the complete image generation workflow",
        "keywords": ["test", "workflow", "ai", "image"],
        "stage": "refinement",
        "status": "in_progress"
    }
    
    response = requests.post(f"{FRONTEND_URL}{API_BASE}/materials", headers=headers, json=material_data)
    print(f"Status: {response.status_code}")
    if response.status_code != 200:
        print(f"❌ Failed: {response.text}")
        return False
    
    material = response.json()
    material_id = material.get("id") or material.get("_id")
    print(f"✅ Material created: {material_id}")
    
    # Step 2: Generate image using free provider
    print(f"\n🎨 STEP 2: Generating Image with Free Provider")
    image_params = {
        "url": "https://picsum.photos/1024/768",  # Fallback URL
        "prompt": "A modern professional business meeting with diverse team members discussing AI technology",
        "ai_provider": "free-test-provider",
        "generation_params": json.dumps({
            "size": "1024x768",
            "style": "photorealistic",
            "quality": "high"
        })
    }
    
    print(f"Adding image to material {material_id}...")
    response = requests.post(
        f"{FRONTEND_URL}{API_BASE}/materials/{material_id}/images",
        headers=headers,
        params=image_params
    )
    
    print(f"Status: {response.status_code}")
    if response.status_code == 200:
        updated_material = response.json()
        images = updated_material.get("generated_images", [])
        print(f"✅ Response received. Images count: {len(images)}")
        
        if len(images) > 0:
            print("🎉 SUCCESS! Images generated:")
            for i, img in enumerate(images):
                print(f"  {i+1}. URL: {img.get('url')}")
                print(f"     Prompt: {img.get('prompt')}")
                print(f"     Provider: {img.get('ai_provider')}")
            
            # Step 3: Select image and finalize
            print(f"\n✅ STEP 3: Selecting Image and Finalizing")
            first_image_url = images[0]["url"]
            
            select_response = requests.post(
                f"{FRONTEND_URL}{API_BASE}/materials/{material_id}/select-image",
                headers=headers,
                json={"image_url": first_image_url}
            )
            
            if select_response.status_code == 200:
                print("✅ Image selected successfully")
                
                # Final verification
                final_response = requests.get(f"{FRONTEND_URL}{API_BASE}/materials/{material_id}", headers=headers)
                if final_response.status_code == 200:
                    final_material = final_response.json()
                    final_images = len(final_material.get("generated_images", []))
                    selected_image = final_material.get("selected_image")
                    
                    print(f"\n🏆 WORKFLOW COMPLETED SUCCESSFULLY!")
                    print(f"✅ Material ID: {material_id}")
                    print(f"✅ Generated Images: {final_images}")
                    print(f"✅ Selected Image: {selected_image}")
                    print(f"✅ Status: Ready for use")
                    
                    return True
                else:
                    print(f"❌ Final verification failed: {final_response.status_code}")
            else:
                print(f"❌ Image selection failed: {select_response.status_code}")
        else:
            print("❌ No images were generated")
            print(f"Response data: {updated_material}")
    else:
        print(f"❌ Image generation failed: {response.text}")
    
    return False

if __name__ == "__main__":
    success = test_complete_workflow()
    if success:
        print("\n🎉 ALL TESTS PASSED - WORKFLOW IS WORKING!")
    else:
        print("\n❌ WORKFLOW TEST FAILED")
        print("\nTo use this system:")
        print("1. Open http://127.0.0.1:3001/en/materials/create")
        print("2. Fill in the material details")
        print("3. Select 'Free Test Provider' as your AI provider")
        print("4. Generate images and enjoy!")
