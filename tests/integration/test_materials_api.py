import requests
import json
import os
import traceback
import sys

def test_materials_api():
    """Test the materials API endpoints to see if they work properly."""
    # Unset proxy for local requests
    os.environ["HTTP_PROXY"] = ""
    os.environ["HTTPS_PROXY"] = ""
    os.environ["NO_PROXY"] = "*"
    
    # Use a token that we know will work with the mock database
    print("Using development mock token...")
    # This token matches one of the hardcoded tokens in deps.py
    token = "eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9.eyJzdWIiOiJ0ZXN0QGV4YW1wbGUuY29tIiwibmFtZSI6IlRlc3QgVXNlciIsImlhdCI6MTY5NDYxMjMxMCwiZXhwIjo0ODQ4MzcyMzEwfQ.YourSignatureHere"
    
    # First test the diagnostic endpoint to verify the API is working
    print("\nTesting diagnostic endpoint...")
    ping_url = "http://127.0.0.1:8088/api/v1/diagnostic/ping"
    ping_response = requests.get(ping_url)
    print(f"Ping status: {ping_response.status_code}")
    print(f"Ping response: {ping_response.text}")
    
    # Test the current user endpoint to see if auth is working
    print("\nTesting current user endpoint...")
    headers = {"Authorization": f"Bearer {token}"}
    user_url = "http://127.0.0.1:8089/api/v1/users/me"
    user_response = requests.get(user_url, headers=headers)
    print(f"User status: {user_response.status_code}")
    if user_response.status_code == 200:
        user_data = user_response.json()
        print(f"User data: {json.dumps(user_data, indent=2)}")
    else:
        print(f"User error: {user_response.text}")
    
    try:
        # Skip the token fetching and use our known working token
        
        # Test GET /materials endpoint
        print("\nTesting materials list endpoint...")
        headers = {"Authorization": f"Bearer {token}"}
        materials_url = "http://127.0.0.1:8089/api/v1/materials"
        
        list_response = requests.get(materials_url, headers=headers)
        print(f"Status code: {list_response.status_code}")
        if list_response.status_code == 200:
            materials = list_response.json()
            print(f"Got {len(materials)} materials")
        else:
            print(f"Error: {list_response.text}")
            
        # Create a test material
        print("\nTesting material creation...")
        new_material = {
            "title": "Test Material",
            "description": "This is a test material",
            "content": "Test content",
            "marketing_goal": "Testing the API",
            "target_audience": "Developers",
            "stage": "draft",
            "status": "in_progress"
        }
        
        create_response = requests.post(materials_url, json=new_material, headers=headers)
        print(f"Status code: {create_response.status_code}")
        if create_response.status_code == 200:
            created = create_response.json()
            print(f"Created material with ID: {created.get('_id')}")
            
            # Test getting a specific material
            print("\nTesting get specific material...")
            material_id = created.get('_id')
            detail_response = requests.get(f"{materials_url}/{material_id}", headers=headers)
            print(f"Status code: {detail_response.status_code}")
            if detail_response.status_code == 200:
                material = detail_response.json()
                print(f"Got material: {material.get('title')}")
            else:
                print(f"Error: {detail_response.text}")
        else:
            print(f"Error: {create_response.text}")
            
    except Exception as e:
        print(f"Exception occurred: {str(e)}")

if __name__ == "__main__":
    try:
        test_materials_api()
    except Exception as e:
        print(f"\nERROR: {str(e)}")
        print("\nTraceback:")
        traceback.print_exc()
        sys.exit(1)
