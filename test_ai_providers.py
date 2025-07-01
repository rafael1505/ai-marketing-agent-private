#!/usr/bin/env python3
"""
Test script for AI Providers functionality
Tests the complete CRUD operations and validation
"""

import requests
import json
import sys

BASE_URL = "http://127.0.0.1:8088/api/v1/ai-providers"
HEADERS = {
    "accept": "application/json",
    "Content-Type": "application/json",
    "Authorization": "Bearer mock_test_token"
}

def test_get_providers():
    """Test getting all providers"""
    print("🔍 Testing GET /ai-providers...")
    response = requests.get(BASE_URL, headers=HEADERS)
    if response.status_code == 200:
        providers = response.json()
        print(f"✅ Successfully retrieved {len(providers)} providers")
        for provider in providers:
            print(f"  - {provider['name']} ({provider['id']}) - Configured: {provider['isConfigured']}")
        return providers
    else:
        print(f"❌ Failed to get providers: {response.status_code} - {response.text}")
        return []

def test_validate_api_key(provider_id, api_key):
    """Test API key validation"""
    print(f"🔑 Testing API key validation for {provider_id}...")
    data = {
        "providerId": provider_id,
        "apiKey": api_key
    }
    response = requests.post(f"{BASE_URL}/validate", headers=HEADERS, json=data)
    if response.status_code == 200:
        result = response.json()
        status = "✅ Valid" if result["valid"] else "❌ Invalid"
        print(f"  {status}: {result['message']}")
        return result["valid"]
    else:
        print(f"❌ Validation failed: {response.status_code} - {response.text}")
        return False

def test_create_provider():
    """Test creating a new provider"""
    print("➕ Testing POST /ai-providers (create)...")
    new_provider = {
        "name": "Test Provider",
        "id": "test-provider-123",
        "apiKey": "sk-test123456789",
        "isConfigured": True,
        "selectedModel": "test-model-v1",
        "maxTokens": 2000,
        "temperature": 0.8,
        "isActive": True
    }
    
    response = requests.post(BASE_URL, headers=HEADERS, json=new_provider)
    if response.status_code == 200:
        created = response.json()
        print(f"✅ Successfully created provider: {created['name']}")
        print(f"  API Key masked: {created.get('apiKey', 'None')}")
        return created
    else:
        print(f"❌ Failed to create provider: {response.status_code} - {response.text}")
        return None

def test_update_provider(provider_id):
    """Test updating a provider"""
    print(f"📝 Testing PUT /ai-providers/{provider_id} (update)...")
    updates = {
        "selectedModel": "updated-model-v2",
        "maxTokens": 3000,
        "temperature": 0.9
    }
    
    response = requests.put(f"{BASE_URL}/{provider_id}", headers=HEADERS, json=updates)
    if response.status_code == 200:
        updated = response.json()
        print(f"✅ Successfully updated provider: {updated['name']}")
        print(f"  New model: {updated['selectedModel']}")
        return updated
    else:
        print(f"❌ Failed to update provider: {response.status_code} - {response.text}")
        return None

def test_get_provider_options(provider_id):
    """Test getting provider options"""
    print(f"⚙️ Testing GET /ai-providers/{provider_id}/options...")
    response = requests.get(f"{BASE_URL}/{provider_id}/options", headers=HEADERS)
    if response.status_code == 200:
        options = response.json()
        models = options.get("models", [])
        print(f"✅ Retrieved {len(models)} models for {provider_id}")
        for model in models[:3]:  # Show first 3 models
            print(f"  - {model}")
        return options
    else:
        print(f"❌ Failed to get options: {response.status_code} - {response.text}")
        return None

def test_delete_provider(provider_id):
    """Test deleting a provider"""
    print(f"🗑️ Testing DELETE /ai-providers/{provider_id}...")
    response = requests.delete(f"{BASE_URL}/{provider_id}", headers=HEADERS)
    if response.status_code == 200:
        result = response.json()
        print(f"✅ Successfully deleted provider: {provider_id}")
        return True
    else:
        print(f"❌ Failed to delete provider: {response.status_code} - {response.text}")
        return False

def main():
    """Run comprehensive tests"""
    print("🚀 Starting AI Providers API Tests")
    print("=" * 50)
    
    # Test 1: Get initial providers
    initial_providers = test_get_providers()
    print()
    
    # Test 2: Validate API keys
    test_validate_api_key("stability", "sk-valid123")
    test_validate_api_key("stability", "invalid-key")  # Should fail
    test_validate_api_key("huggingface", "hf_valid123")
    print()
    
    # Test 3: Get provider options
    test_get_provider_options("stability")
    test_get_provider_options("huggingface")
    print()
    
    # Test 4: Create new provider
    created_provider = test_create_provider()
    print()
    
    if created_provider:
        provider_id = created_provider["id"]
        
        # Test 5: Update the provider
        test_update_provider(provider_id)
        print()
        
        # Test 6: Get updated providers list
        test_get_providers()
        print()
        
        # Test 7: Delete the test provider
        test_delete_provider(provider_id)
        print()
        
        # Test 8: Verify deletion
        final_providers = test_get_providers()
        print()
    
    print("✨ AI Providers API testing completed!")

if __name__ == "__main__":
    try:
        main()
    except KeyboardInterrupt:
        print("\n⚠️ Tests interrupted by user")
        sys.exit(1)
    except Exception as e:
        print(f"\n💥 Test failed with error: {e}")
        sys.exit(1)
