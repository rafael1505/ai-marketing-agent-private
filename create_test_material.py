import json
import requests
from pprint import pprint

def create_test_material():
    print("Creating test material...")
    
    # Get the token from the JSON file
    with open("auth_token.json", "r") as f:
        auth_data = json.load(f)
    
    token = auth_data.get("token", "DEVELOPMENT_MOCK_TOKEN_FOR_TESTING")
    print(f"Using token: {token}")
    
    # Set up the headers
    headers = {
        "Authorization": f"Bearer {token}",
        "Content-Type": "application/json"
    }
    
    # Create test material data
    data = {
        "title": "Test Marketing Material",
        "description": "A test material created via API",
        "target_audience": "Developers and testers",
        "campaign_objective": "Testing the material creation endpoint",
        "keywords": ["test", "api", "material"],
        "stage": "idea",
        "status": "draft"
    }
    
    # Make the API call
    url = "http://localhost:8088/api/v1/materials"
    print(f"Sending POST to {url}")
    print(f"Headers: {headers}")
    print(f"Data: {json.dumps(data)}")
    
    try:
        response = requests.post(url, headers=headers, json=data, timeout=10)
        response.raise_for_status()
        
        print(f"Status code: {response.status_code}")
        print(f"Headers: {response.headers}")
        
        material = response.json()
        print("Material created successfully:")
        pprint(material)
        
        print(f"\nMaterial ID: {material.get('_id', 'N/A')}")
        print(f"Edit URL: http://localhost:3001/en/materials/{material.get('_id', 'N/A')}/edit")
        
        return material
    except requests.exceptions.HTTPError as e:
        print(f"Status code: {e.response.status_code}")
        print(f"Headers: {e.response.headers}")
        print(f"Content: {e.response.content.decode('utf-8')}")
        print("Error creating material")
        return None
    except Exception as e:
        print(f"Error: {str(e)}")
        return None

if __name__ == "__main__":
    material = create_test_material()
    
    if material:
        print("\n===== SUCCESS =====")
        print(f"Material ID: {material.get('_id')}")
        print(f"Material title: {material.get('title')}")
        material_id = material.get('_id')
        print(f"\nEdit URL: http://localhost:3001/en/materials/{material_id}/edit")
        print(f"View URL: http://localhost:3001/en/materials/{material_id}")
    else:
        print("\n===== FAILED =====")
        print("Failed to create test material")
