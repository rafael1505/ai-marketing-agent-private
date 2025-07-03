#!/usr/bin/env python3

import requests
import json
import os

# Set proxy environment to bypass proxy for localhost
os.environ['NO_PROXY'] = 'localhost,127.0.0.1'

def test_workflow():
    base_url = "http://localhost:8089"
    
    # Test 1: Check if server is running
    try:
        response = requests.get(f"{base_url}/")
        print(f"✓ Server is running (got {response.status_code})")
    except Exception as e:
        print(f"✗ Server connection failed: {e}")
        return
    
    # Generate a simple JWT token manually for testing
    import jwt
    from datetime import datetime, timedelta
    
    secret_key = "default_secret_key_change_in_production"
    token_data = {
        "sub": "test-user-123",
        "company_id": "test-company-123",
        "exp": datetime.utcnow() + timedelta(hours=24)
    }
    
    token = jwt.encode(token_data, secret_key, algorithm="HS256")
    
    # Test 2: Create a material with ideation
    print("\n--- Testing Material Creation ---")
    
    headers = {
        "Content-Type": "application/json",
        "Authorization": f"Bearer {token}"
    }
    
    material_data = {
        "title": "Test Marketing Material",
        "description": "A test marketing material for workflow verification",
        "target_audience": "Tech professionals",
        "campaign_objective": "Brand awareness",
        "keywords": ["innovation", "technology", "professional"],
        "company_id": "test-company-123"
    }
    
    try:
        response = requests.post(f"{base_url}/api/v1/materials/", 
                               json=material_data, 
                               headers=headers)
        
        if response.status_code == 201:
            material = response.json()
            material_id = material["id"]
            print(f"✓ Material created successfully: {material_id}")
            
            # Test 3: Generate image with Free Test Provider
            print("\n--- Testing Image Generation ---")
            
            image_data = {
                "prompt": "A professional tech workspace with modern computers and sleek design",
                "ai_provider": "free-test-provider"
            }
            
            response = requests.post(f"{base_url}/api/v1/materials/{material_id}/generate-image", 
                                   json=image_data, 
                                   headers=headers)
            
            if response.status_code == 200:
                result = response.json()
                print(f"✓ Image generated successfully!")
                print(f"  Provider: {result.get('ai_provider')}")
                print(f"  Image URL: {result.get('image_url')}")
                
                # Test 4: Get updated material
                response = requests.get(f"{base_url}/api/v1/materials/{material_id}", 
                                      headers=headers)
                
                if response.status_code == 200:
                    updated_material = response.json()
                    images = updated_material.get("generated_images", [])
                    print(f"✓ Material updated with {len(images)} generated image(s)")
                    
                    print("\n--- Workflow Test Completed Successfully! ---")
                    return True
                else:
                    print(f"✗ Failed to get updated material: {response.status_code}")
                    print(f"Response: {response.text}")
            else:
                print(f"✗ Image generation failed: {response.status_code}")
                print(f"Response: {response.text}")
        else:
            print(f"✗ Material creation failed: {response.status_code}")
            print(f"Response: {response.text}")
            
    except Exception as e:
        print(f"✗ Request failed: {e}")
    
    return False

if __name__ == "__main__":
    print("=== AI Marketing Agent Workflow Test ===")
    success = test_workflow()
    exit(0 if success else 1)
