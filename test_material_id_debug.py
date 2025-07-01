#!/usr/bin/env python3
"""
This script runs a quick test of the materials API to analyze what's happening with IDs
"""
import requests
import json
import sys
import os
from pprint import pprint

# Development mock token
DEV_TOKEN = "DEVELOPMENT_MOCK_TOKEN_FOR_TESTING"

# Make sure we're not using a proxy for localhost
os.environ['no_proxy'] = 'localhost,127.0.0.1'
if 'http_proxy' in os.environ:
    del os.environ['http_proxy']
if 'https_proxy' in os.environ:
    del os.environ['https_proxy']

def print_separator():
    print("-" * 80)

def test_create():
    print("Creating a test material...")
    headers = {
        "Authorization": f"Bearer {DEV_TOKEN}",
        "Content-Type": "application/json"
    }
    
    material_data = {
        "title": "Test Material - " + str(sys.argv[1]) if len(sys.argv) > 1 else "Default Test",
        "description": "Test description",
        "target_audience": "Test audience",
        "campaign_objective": "Test objective",
        "keywords": ["test", "api"],
        "stage": "idea",
        "status": "draft"
    }
    
    response = requests.post(
        "http://127.0.0.1:8088/api/v1/materials",
        headers=headers,
        json=material_data
    )
    
    print(f"Status: {response.status_code}")
    if response.status_code == 200:
        result = response.json()
        print("Response JSON:")
        pprint(result)
        
        material_id = result.get("id") or result.get("_id")
        if material_id:
            print(f"Material ID: {material_id} (type: {type(material_id).__name__})")
            return material_id
        else:
            print("No material ID found in response")
    else:
        print(f"Error: {response.text}")
    return None

def test_get(material_id):
    print_separator()
    print(f"Fetching material with ID: {material_id}")
    headers = {"Authorization": f"Bearer {DEV_TOKEN}"}
    
    response = requests.get(
        f"http://127.0.0.1:8088/api/v1/materials/{material_id}",
        headers=headers
    )
    
    print(f"Status: {response.status_code}")
    try:
        result = response.json()
        print("Response JSON:")
        pprint(result)
    except:
        print(f"Raw response: {response.text}")

def test_list():
    print_separator()
    print("Listing all materials:")
    headers = {"Authorization": f"Bearer {DEV_TOKEN}"}
    
    response = requests.get(
        "http://127.0.0.1:8088/api/v1/materials",
        headers=headers
    )
    
    print(f"Status: {response.status_code}")
    try:
        result = response.json()
        print("Response JSON:")
        pprint(result)
    except:
        print(f"Raw response: {response.text}")

if __name__ == "__main__":
    material_id = test_create()
    if material_id:
        test_get(material_id)
        
        # Try different variations of the ID
        if str(material_id).isdigit():
            test_get(int(material_id))
    
    test_list()
