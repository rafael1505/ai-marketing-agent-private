#!/usr/bin/env python3
"""
Test script to verify that material creation works correctly.
This version uses the existing development token.
"""

import requests
import json
import sys
from pprint import pprint

def get_auth_token():
    # Use development token
    token = "DEVELOPMENT_MOCK_TOKEN_FOR_TESTING"
    print(f"Using token: {token}")
    return token

def test_material_creation():
    token = get_auth_token()
    if not token:
        print("Authentication token is required")
        return False
    
    headers = {
        "Authorization": f"Bearer {token}",
        "Content-Type": "application/json"
    }
    print(f"Using headers: {headers}")
    
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
    print(f"Material data: {json.dumps(material_data)}")
    
    print("Creating test material...")
    try:
        response = requests.post(
            "http://localhost:8088/api/v1/materials",
            headers=headers,
            json=material_data
        )
        
        print(f"Status code: {response.status_code}")
        print(f"Response headers: {response.headers}")
        print(f"Raw response: {response.text[:500]}...")  # Print first 500 chars of response
        
        if response.status_code == 200:
            result = response.json()
            print("Response:")
            pprint(result)
            
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
    print(f"Using headers for list: {headers}")
    
    print("\nListing all materials...")
    url = "http://localhost:8088/api/v1/materials"
    print(f"Request URL: {url}")
    
    try:
        response = requests.get(
            url,
            headers=headers
        )
        
        print(f"Status code: {response.status_code}")
        print(f"Response headers: {response.headers}")
        print(f"Raw response: {response.text[:500]}...")  # Print first 500 chars
        
        try:
            result = response.json()
            print(f"Response JSON ({type(result)}):")
            pprint(result)
            return response.status_code == 200
        except Exception as e:
            print(f"Error parsing response as JSON: {e}")
            print(f"Full raw response: {response.text}")
            return False
    except Exception as e:
        print(f"Error making request: {e}")
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
