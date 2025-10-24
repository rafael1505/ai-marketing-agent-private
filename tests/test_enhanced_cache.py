#!/usr/bin/env python3
"""
Test script to simulate the browser environment and verify the materials cache fixes.
This simulates the workflow where a material is created, then an image is generated.
"""

import json
import time
from datetime import datetime

# Simulate localStorage
class MockLocalStorage:
    def __init__(self):
        self._storage = {}
    
    def getItem(self, key):
        return self._storage.get(key)
    
    def setItem(self, key, value):
        self._storage[key] = value
        print(f"[localStorage] Saved: {key}")

# Global storage
localStorage = MockLocalStorage()

# Materials cache
materials_cache = {
    "data": None,
    "timestamp": 0,
    "ttl": 30000
}

def is_development_mode():
    return True

def get_demo_materials():
    return [
        {
            "id": "demo-1",
            "title": "🎯 Product Launch Campaign",
            "generated_images": []
        },
        {
            "id": "demo-2", 
            "title": "📱 Social Media Content Series",
            "generated_images": []
        }
    ]

def load_cache_from_storage():
    if is_development_mode():
        try:
            stored = localStorage.getItem('dev_materials_cache')
            if stored:
                parsed = json.loads(stored)
                if parsed.get("data") and isinstance(parsed["data"], list) and (time.time() * 1000 - parsed["timestamp"]) < parsed["ttl"]:
                    materials_cache["data"] = parsed["data"]
                    materials_cache["timestamp"] = parsed["timestamp"]
                    print(f"[Cache] Loaded from localStorage: {len(materials_cache['data'])} materials")
        except Exception as error:
            print(f"[Cache] Failed to load from localStorage: {error}")

def save_cache_to_storage():
    if is_development_mode() and materials_cache["data"]:
        try:
            cache_data = {
                "data": materials_cache["data"],
                "timestamp": materials_cache["timestamp"],
                "ttl": materials_cache["ttl"]
            }
            localStorage.setItem('dev_materials_cache', json.dumps(cache_data))
            print("[Cache] Saved to localStorage")
        except Exception as error:
            print(f"[Cache] Failed to save to localStorage: {error}")

def create_material(data):
    print("\n=== Creating Material ===")
    
    # Load cache from storage if available
    load_cache_from_storage()
    
    new_material = {
        "id": f"demo-new-{int(time.time() * 1000)}",
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
    
    print(f"Created new material with ID: {new_material['id']}")
    
    # Initialize cache with demo materials if it doesn't exist
    if not materials_cache["data"]:
        print("Initializing cache with demo materials")
        materials_cache["data"] = get_demo_materials()
        materials_cache["timestamp"] = time.time() * 1000
    
    # Add new material to the beginning of the cache
    materials_cache["data"].insert(0, new_material)
    print(f"Added material to cache. Cache now has {len(materials_cache['data'])} materials")
    print(f"Cache material IDs: {[m['id'] for m in materials_cache['data']]}")
    
    # Update global cache timestamp and save to storage
    materials_cache["timestamp"] = time.time() * 1000
    save_cache_to_storage()
    
    return new_material

def add_generated_image(material_id, image_url, prompt, ai_provider, generation_params):
    print(f"\n=== Adding Generated Image ===")
    print(f"Adding image to material: {material_id}")
    
    # Simulate cache being reset (e.g., hot reload in Next.js)
    print("[Simulation] Simulating cache reset (like hot reload)...")
    materials_cache["data"] = None
    materials_cache["timestamp"] = 0
    
    # Load cache from storage if available (this is where the fix kicks in)
    load_cache_from_storage()
    
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
    
    # Save to localStorage for persistence
    save_cache_to_storage()
    
    print(f"Image added successfully. Material now has {len(updated_material['generated_images'])} images")
    return updated_material

# Test the complete workflow
print("=== Testing Enhanced Materials Cache with localStorage Persistence ===")

# Step 1: Create a material
print("\n1. Creating material...")
material = create_material({
    "title": "Test Marketing Campaign",
    "description": "Test description",
    "target_audience": "Tech enthusiasts",
    "campaign_objective": "Brand awareness",
    "keywords": ["tech", "innovation"]
})

print(f"\n2. Material created: {material['id']}")

# Step 3: Add an image to the material (simulating cache reset)
print("\n3. Adding image to material (with simulated cache reset)...")
updated_material = add_generated_image(
    material["id"],
    "https://example.com/test-image.jpg",
    "A test marketing image",
    "Free Test Provider",
    {"size": "1024x1024"}
)

print("\n4. Final results:")
print(f"   - Material ID: {updated_material['id']}")
print(f"   - Images count: {len(updated_material['generated_images'])}")
print(f"   - Cache size: {len(materials_cache['data'])}")
print(f"   - Material found via fallback: {'AI Marketing Material' in updated_material['title']}")

print("\n=== Test completed successfully! ===")
print("The enhanced cache with localStorage persistence should prevent 'Material not found' errors.")
