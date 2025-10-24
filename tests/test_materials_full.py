import requests
import os
import json
import time

# Wait for the server to start
print("Waiting for API server to start...")
time.sleep(3)

# Disable proxy for local connections
os.environ["HTTP_PROXY"] = ""
os.environ["HTTPS_PROXY"] = ""
os.environ["NO_PROXY"] = "*"

# Use the test token from deps.py
token = "eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9.eyJzdWIiOiJ0ZXN0QGV4YW1wbGUuY29tIiwibmFtZSI6IlRlc3QgVXNlciIsImlhdCI6MTY5NDYxMjMxMCwiZXhwIjo0ODQ4MzcyMzEwfQ.YourSignatureHere"

# Test the diagnostic endpoint first
print("\nTesting diagnostic endpoint...")
try:
    response = requests.get("http://127.0.0.1:8088/api/v1/diagnostic/ping")
    print(f"Status: {response.status_code}")
    print(f"Response: {response.text}")
    
    if response.status_code != 200:
        print("ERROR: Diagnostic endpoint not working!")
        exit(1)
except Exception as e:
    print(f"ERROR connecting to API: {str(e)}")
    exit(1)

# Test the materials endpoint
print("\nTesting materials list endpoint...")
headers = {"Authorization": f"Bearer {token}"}
materials_url = "http://127.0.0.1:8088/api/v1/materials"

try:
    response = requests.get(materials_url, headers=headers)
    print(f"Status code: {response.status_code}")
    if response.status_code == 200:
        materials = response.json()
        print(f"Got {len(materials)} materials")
        if len(materials) == 0:
            print("Materials list is empty - this is expected for a fresh database")
        else:
            print(f"First material: {json.dumps(materials[0], indent=2)}")
    else:
        print(f"Error: {response.text}")
        exit(1)
except Exception as e:
    print(f"Exception: {str(e)}")
    exit(1)

# Let's create a test material
print("\nCreating a test material...")
new_material = {
    "title": "Test Material",
    "description": "This is a test material",
    "content": "Test content for API",
    "marketing_goal": "Testing the API fixes",
    "target_audience": "Developers",
    "stage": "draft",
    "status": "in_progress"
}

try:
    response = requests.post(materials_url, json=new_material, headers=headers)
    print(f"Status code: {response.status_code}")
    if response.status_code == 200:
        material = response.json()
        print(f"Created material with ID: {material.get('_id')}")
        material_id = material.get('_id')
        
        # Now fetch this specific material
        print("\nFetching the created material...")
        detail_url = f"{materials_url}/{material_id}"
        detail_response = requests.get(detail_url, headers=headers)
        
        print(f"Status code: {detail_response.status_code}")
        if detail_response.status_code == 200:
            fetched = detail_response.json()
            print(f"Fetched material title: {fetched.get('title')}")
            print("TEST SUCCESSFUL!")
        else:
            print(f"Error fetching material: {detail_response.text}")
            exit(1)
    else:
        print(f"Error creating material: {response.text}")
        exit(1)
except Exception as e:
    print(f"Exception: {str(e)}")
    exit(1)
