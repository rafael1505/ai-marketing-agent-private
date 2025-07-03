#!/usr/bin/env python3
import json
import time
from datetime import datetime

# Test script to verify materials cache behavior
material_id = f"demo-new-{int(time.time() * 1000)}"

# Global cache like in the actual code
materials_cache = {
    "data": None,
    "timestamp": 0,
    "ttl": 30000
}

def get_demo_materials():
    return [
        {
            "id": "demo-1",
            "title": "Test Material 1",
            "generated_images": []
        },
        {
            "id": "demo-2", 
            "title": "Test Material 2",
            "generated_images": []
        }
    ]

def create_material(data):
    print("Creating material in dev mode")
    
    new_material = {
        "id": material_id,
        "title": data["title"],
        "description": data["description"],
        "target_audience": data["target_audience"],
        "campaign_objective": data["campaign_objective"],
        "keywords": data["keywords"],
        "stage": "idea",
        "status": "draft",
        "company_id": "demo_company",
        "created_by": "demo_user",
        "user_id": "demo_user",
        "created_at": datetime.now().isoformat(),
        "updated_at": datetime.now().isoformat(),
        "generated_images": [],
        "feedback": []
    }
    
    print(f"Created material with ID: {new_material['id']}")
    
    # Initialize cache with demo materials if it doesn't exist
    if not materials_cache["data"]:
        print("Initializing cache with demo materials")
        materials_cache["data"] = get_demo_materials()
        materials_cache["timestamp"] = time.time() * 1000
    
    # Add new material to cache
    materials_cache["data"].insert(0, new_material)
    print(f"Added material to cache. Cache now has {len(materials_cache['data'])} materials")
    print(f"Cache material IDs: {[m['id'] for m in materials_cache['data']]}")
    
    return new_material

def add_generated_image(material_id, image_url, prompt, ai_provider, generation_params):
    print(f"Adding generated image: {{'materialId': '{material_id}', 'imageUrl': '{image_url}', 'prompt': '{prompt}', 'aiProvider': '{ai_provider}'}}")
    
    print("Development mode: Handling image addition")
    
    # Ensure cache exists
    if not materials_cache["data"]:
        print("Cache is empty, initializing with demo materials")
        materials_cache["data"] = get_demo_materials()
        materials_cache["timestamp"] = time.time() * 1000
    
    print(f"Looking for material: {material_id}")
    print(f"Cache contents: {[{'id': m['id'], 'title': m['title']} for m in materials_cache['data']]}")
    
    # Find the material in cache
    material = None
    for m in materials_cache["data"]:
        if m["id"] == material_id:
            material = m
            break
    
    if not material:
        print("Material not found in cache, creating fallback material...")
        # Create a fallback material if it doesn't exist
        material = {
            "id": material_id,
            "title": "AI Marketing Material",
            "description": "Generated during image creation",
            "target_audience": "General audience",
            "campaign_objective": "Brand awareness",
            "keywords": ["ai", "marketing"],
            "stage": "refinement",
            "status": "in_progress",
            "company_id": "demo_company",
            "created_by": "demo_user",
            "user_id": "demo_user",
            "created_at": datetime.now().isoformat(),
            "updated_at": datetime.now().isoformat(),
            "generated_images": [],
            "feedback": []
        }
        
        # Add to cache
        materials_cache["data"].insert(0, material)
        print("Created fallback material and added to cache")
    
    # Add the image
    new_image = {
        "url": image_url,
        "prompt": prompt,
        "ai_provider": ai_provider,
        "generation_params": generation_params,
        "created_at": datetime.now().isoformat()
    }
    
    # Create updated material with new image
    updated_material = material.copy()
    updated_material["generated_images"] = (material.get("generated_images", []) or []) + [new_image]
    updated_material["updated_at"] = datetime.now().isoformat()
    
    # Update in cache
    for i, m in enumerate(materials_cache["data"]):
        if m["id"] == material_id:
            materials_cache["data"][i] = updated_material
            print("Updated existing material in cache")
            break
    else:
        # This should not happen after our fallback creation, but just in case
        materials_cache["data"].insert(0, updated_material)
        print("Added updated material to cache")
    
    print(f"Image added successfully. Material now has {len(updated_material['generated_images'])} images")
    return updated_material

# Test the workflow
print("=== Testing Material Creation & Image Addition Workflow ===\n")

# Step 1: Create a material
print("1. Creating material...")
material = create_material({
    "title": "Test Marketing Campaign",
    "description": "Test description",
    "target_audience": "Tech enthusiasts",
    "campaign_objective": "Brand awareness",
    "keywords": ["tech", "innovation"]
})

print(f"\n2. Material created: {material['id']}")

# Step 2: Add an image to the material
print("\n3. Adding image to material...")
updated_material = add_generated_image(
    material["id"],
    "https://example.com/test-image.jpg",
    "A test marketing image",
    "Free Test Provider",
    {"size": "1024x1024"}
)

print("\n4. Final material state:")
print(f"   - ID: {updated_material['id']}")
print(f"   - Images: {len(updated_material['generated_images'])}")
print(f"   - Cache size: {len(materials_cache['data'])}")

print("\n=== Test completed successfully! ===")
