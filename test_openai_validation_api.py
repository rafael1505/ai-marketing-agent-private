#!/usr/bin/env python3
"""
Simple test script to validate OpenAI configuration API endpoint
"""
import requests
import json

def test_openai_validation():
    """Test the OpenAI configuration validation endpoint"""
    
    base_url = "http://localhost:8088"
    
    # Test 1: Valid OpenAI configuration
    print("Testing valid OpenAI configuration...")
    valid_config = {
        "apiKey": "sk-test-valid-key-1234567890abcdef",
        "selectedModel": "dall-e-3",
        "quality": "standard",
        "size": "1024x1024",
        "style": "vivid",
        "isActive": True
    }
    
    try:
        response = requests.post(
            f"{base_url}/api/v1/ai-providers/validate-config",
            params={"provider_id": "openai"},
            json=valid_config,
            timeout=10
        )
        print(f"Status: {response.status_code}")
        if response.status_code == 200:
            result = response.json()
            print(f"Valid: {result.get('valid')}")
            print(f"Errors: {result.get('errors', [])}")
            print(f"Warnings: {result.get('warnings', [])}")
            print(f"Recommendations: {result.get('recommendations', [])}")
        else:
            print(f"Error: {response.text}")
    except requests.exceptions.RequestException as e:
        print(f"Connection error: {e}")
    
    print("\n" + "="*50 + "\n")
    
    # Test 2: Invalid OpenAI configuration
    print("Testing invalid OpenAI configuration...")
    invalid_config = {
        "apiKey": "invalid-key-format",
        "selectedModel": "invalid-model",
        "quality": "ultra-hd",
        "size": "2048x2048",
        "style": "photorealistic"
    }
    
    try:
        response = requests.post(
            f"{base_url}/api/v1/ai-providers/validate-config",
            params={"provider_id": "openai"},
            json=invalid_config,
            timeout=10
        )
        print(f"Status: {response.status_code}")
        if response.status_code == 200:
            result = response.json()
            print(f"Valid: {result.get('valid')}")
            print(f"Errors: {result.get('errors', [])}")
            print(f"Warnings: {result.get('warnings', [])}")
        else:
            print(f"Error: {response.text}")
    except requests.exceptions.RequestException as e:
        print(f"Connection error: {e}")
    
    print("\n" + "="*50 + "\n")
    
    # Test 3: API key validation
    print("Testing API key validation...")
    try:
        response = requests.post(
            f"{base_url}/api/v1/ai-providers/validate",
            json={
                "providerId": "openai",
                "apiKey": "sk-test-key-12345"
            },
            timeout=10
        )
        print(f"Status: {response.status_code}")
        if response.status_code == 200:
            result = response.json()
            print(f"Valid: {result.get('valid')}")
            print(f"Message: {result.get('message')}")
        else:
            print(f"Error: {response.text}")
    except requests.exceptions.RequestException as e:
        print(f"Connection error: {e}")

if __name__ == "__main__":
    test_openai_validation()
