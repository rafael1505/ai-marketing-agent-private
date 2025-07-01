#!/usr/bin/env python3
"""
Test script to verify that material creation works correctly.
"""

import requests
import json
import sys
from pprint import pprint

def get_auth_token():
    # Load the stored token
    try:
        with open('auth_token.json', 'r') as f:
            token_data = json.load(f)
            return token_data.get('access_token')
    except (FileNotFoundError, json.JSONDecodeError):
        print("No valid auth token found. Please run the authentication test first.")
        sys.exit(1)

def test_material_creation():
    token = get_auth_token()
    if not token:
        print("Authentication token is required")
        return False
    
    headers = {
        "Authorization": f"Bearer {token}",
        "Content-Type": "application/json"
    }
    
    # Create a test material
    material_data = {
        "title": "Test Marketing Material",
        "description": "A test material created via API",
        "target_audience": "Developers and testers",
        "campaign_objective": "Testing the material creation endpoint",
        "keywords": ["test", "api", "material"],
        "stage": "idea",  # Using enum values: idea, refinement, finalization
        "status": "draft"  # Using enum values: draft, in_progress, ready_for_review, completed, archived
    }
    
    print("Creating test material...")
    response = requests.post(
        "http://localhost:8088/api/v1/materials",
        headers=headers,
        json=material_data
    )
    
    print(f"Status code: {response.status_code}")
    
    try:
        result = response.json()
        print("Response:")
        pprint(result)
        
        if response.status_code == 200 and result is not None:
            material_id = result.get("_id") or result.get("id")
            if material_id:
                print(f"Successfully created material with ID: {material_id}")
                
                # Now fetch the material to verify
                print("\nFetching the created material...")
                fetch_response = requests.get(
                    f"http://localhost:8088/api/v1/materials/{material_id}",
                    headers=headers
                )
                
                print(f"Fetch status code: {fetch_response.status_code}")
                try:
                    fetch_result = fetch_response.json()
                    print("Fetched material:")
                    pprint(fetch_result)
                    return fetch_response.status_code == 200 and fetch_result is not None
                except Exception as e:
                    print(f"Error parsing fetch response: {e}")
                    return False
            else:
                print("Error: Created material has no ID")
                return False
        else:
            print("Error creating material")
            return False
    except Exception as e:
        print(f"Error parsing response: {e}")
        print(f"Raw response: {response.text}")
        return False

def list_materials():
    token = get_auth_token()
    if not token:
        print("Authentication token is required")
        return False
    
    headers = {
        "Authorization": f"Bearer {token}"
    }
    
    print("\nListing all materials...")
    response = requests.get(
        "http://localhost:8088/api/v1/materials",
        headers=headers
    )
    
    print(f"Status code: {response.status_code}")
    
    try:
        result = response.json()
        print("Response:")
        pprint(result)
        return response.status_code == 200
    except Exception as e:
        print(f"Error parsing response: {e}")
        print(f"Raw response: {response.text}")
        return False

if __name__ == "__main__":
    print("Testing Material API...")
    success = test_material_creation()
    list_success = list_materials()
    
    if success and list_success:
        print("\nSuccess! Material API is working correctly.")
        sys.exit(0)
    else:
        print("\nError: Material API test failed.")
        sys.exit(1)
