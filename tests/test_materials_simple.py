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

# Test the materials endpoint
print("\nTesting materials list endpoint...")
headers = {"Authorization": f"Bearer {token}"}
print(f"Headers: {headers}")
materials_url = "http://localhost:8088/api/v1/materials"
print(f"URL: {materials_url}")

try:
    response = requests.get(materials_url, headers=headers)
    print(f"Status code: {response.status_code}")
    if response.status_code == 200:
        materials = response.json()
        print(f"Got {len(materials)} materials")
        print(f"Materials data: {json.dumps(materials, indent=2)}")
    else:
        print(f"Error: {response.text}")
except Exception as e:
    print(f"Exception: {str(e)}")

print("\nThis concludes our test")
