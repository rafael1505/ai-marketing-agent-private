import requests
import os
import json

# Disable proxy for local connections
os.environ["HTTP_PROXY"] = ""
os.environ["HTTPS_PROXY"] = ""
os.environ["NO_PROXY"] = "*"

# Use the development mock token - this should work with our auth system
token = "DEVELOPMENT_MOCK_TOKEN_FOR_TESTING"
print(f"Using token: {token}")

# Test creating a material
print("\nTesting material creation endpoint...")
headers = {
    "Authorization": f"Bearer {token}",
    "Content-Type": "application/json"
}
print(f"Headers: {headers}")

# Material data to create
material_data = {
    "title": "Test Material via Simple Test",
    "description": "Created through the simple test script",
    "target_audience": "API testers",
    "campaign_objective": "Verify API works correctly",
    "keywords": ["test", "API", "simple"],
    "stage": "idea",  # Using enum values: idea, refinement, finalization
    "status": "draft"  # Using enum values: draft, in_progress, ready_for_review, completed, archived
}
print(f"Material data: {json.dumps(material_data, indent=2)}")

# Send create request
materials_url = "http://localhost:8088/api/v1/materials"
print(f"URL: {materials_url}")

try:
    response = requests.post(materials_url, headers=headers, json=material_data)
    print(f"Status code: {response.status_code}")
    
    if response.status_code == 200:
        material = response.json()
        print(f"Successfully created material!")
        print(f"Material data: {json.dumps(material, indent=2)}")
        
        # Now fetch the material to verify
        material_id = material.get("_id") or material.get("id")
        if material_id:
            print(f"\nFetching the created material with ID: {material_id}")
            get_url = f"{materials_url}/{material_id}"
            print(f"Fetch URL: {get_url}")
            
            get_response = requests.get(get_url, headers=headers)
            print(f"Fetch status code: {get_response.status_code}")
            
            if get_response.status_code == 200:
                fetched = get_response.json()
                print(f"Successfully fetched material!")
                print(f"Fetched data: {json.dumps(fetched, indent=2)}")
            else:
                print(f"Error fetching material: {get_response.text}")
        else:
            print("Error: Created material has no ID")
    else:
        print(f"Error creating material: {response.text}")
except Exception as e:
    print(f"Exception: {str(e)}")

print("\nThis concludes our test")
