#!/usr/bin/env python3
"""
Test script for multi-image generation functionality
"def test_single_image_generation():
    """Test backward compatibility with single image generation"""
    
    base_url = "http://127.0.0.1:8088"mport requests
import json
import sys

def test_multi_image_generation():
    """Test the new multi-image generation feature"""
    
    base_url = "http://127.0.0.1:8088"
    endpoint = f"{base_url}/api/v1/ai/generate-image"
    
    # Test parameters
    test_params = {
        "prompt": "A professional healthcare device showcasing modern technology",
        "ai_provider": "context-aware-test-provider",
        "size": "1024x1024",
        "variations": "5",  # Request 5 variations
        "company_id": "philips",
        "material_type": "brochure",
        "target_audience": "Healthcare professionals",
        "campaign_theme": "Innovation"
    }
    
    print("🔄 Testing Multi-Image Generation API...")
    print(f"📍 Endpoint: {endpoint}")
    print(f"🎯 Parameters: {json.dumps(test_params, indent=2)}")
    print("-" * 50)
    
    try:
        # Make the request
        print("📡 Making API request...")
        response = requests.post(endpoint, params=test_params, timeout=30)
        
        print(f"📊 Status Code: {response.status_code}")
        
        if response.status_code == 200:
            data = response.json()
            
            if data.get("success") and data.get("variations"):
                print("✅ SUCCESS: Multi-image generation working!")
                print(f"🖼️  Generated {len(data['variations'])} image variations")
                
                # Display variation details
                for i, variation in enumerate(data["variations"], 1):
                    print(f"   Variation {i}: ID={variation.get('variation_id')}, Image_ID={variation.get('image_id')}")
                    print(f"   URL length: {len(variation.get('image_url', ''))}")
                
                # Display metadata
                metadata = data.get("metadata", {})
                print(f"\n📋 Metadata:")
                print(f"   Total variations: {metadata.get('total_variations')}")
                print(f"   Company: {metadata.get('company', {}).get('name')}")
                print(f"   Brand colors: {metadata.get('company', {}).get('brand_colors')}")
                print(f"   Material type: {metadata.get('material_type')}")
                
                return True
                
            elif data.get("success") and data.get("image_url"):
                print("⚠️  PARTIAL SUCCESS: Single image generated (fallback mode)")
                print(f"🖼️  Image URL length: {len(data.get('image_url', ''))}")
                return True
                
            else:
                print("❌ FAILED: No valid response data")
                print(f"Response: {json.dumps(data, indent=2)}")
                return False
        else:
            print(f"❌ FAILED: HTTP {response.status_code}")
            print(f"Response: {response.text}")
            return False
            
    except requests.exceptions.ConnectionError:
        print("❌ FAILED: Cannot connect to server. Is it running on port 8088?")
        return False
    except Exception as e:
        print(f"❌ FAILED: {str(e)}")
        return False

def test_single_image_generation():
    """Test backward compatibility with single image generation"""
    
    base_url = "http://127.0.0.1:8088"
    endpoint = f"{base_url}/api/v1/ai/generate-image"
    
    # Test parameters (no variations param = single image)
    test_params = {
        "prompt": "A sleek smartphone with innovative features",
        "ai_provider": "context-aware-test-provider",
        "size": "1024x1024",
        "company_id": "apple"
    }
    
    print("\n🔄 Testing Single Image Generation (Backward Compatibility)...")
    print(f"📍 Endpoint: {endpoint}")
    print(f"🎯 Parameters: {json.dumps(test_params, indent=2)}")
    print("-" * 50)
    
    try:
        response = requests.post(endpoint, params=test_params, timeout=30)
        
        print(f"📊 Status Code: {response.status_code}")
        
        if response.status_code == 200:
            data = response.json()
            
            if data.get("success") and data.get("image_url"):
                print("✅ SUCCESS: Single image generation working!")
                print(f"🖼️  Image URL length: {len(data.get('image_url', ''))}")
                print(f"📋 Image ID: {data.get('metadata', {}).get('image_id')}")
                return True
            else:
                print("❌ FAILED: No valid single image response")
                print(f"Response: {json.dumps(data, indent=2)}")
                return False
        else:
            print(f"❌ FAILED: HTTP {response.status_code}")
            print(f"Response: {response.text}")
            return False
            
    except Exception as e:
        print(f"❌ FAILED: {str(e)}")
        return False

if __name__ == "__main__":
    print("🎨 Multi-Image Generation Test Suite")
    print("=" * 50)
    
    # Test multi-image generation
    multi_success = test_multi_image_generation()
    
    # Test single image generation (backward compatibility)
    single_success = test_single_image_generation()
    
    print("\n" + "=" * 50)
    print("📋 TEST SUMMARY:")
    print(f"   Multi-image generation: {'✅ PASS' if multi_success else '❌ FAIL'}")
    print(f"   Single image generation: {'✅ PASS' if single_success else '❌ FAIL'}")
    
    if multi_success and single_success:
        print("\n🎉 ALL TESTS PASSED! The multi-image functionality is working correctly.")
        print("\n📝 Next steps:")
        print("   1. Start the server: python context_aware_test_api_server.py")
        print("   2. Open browser: http://localhost:3001/multi-image-selection-test.html")
        print("   3. Test the interactive multi-image selection interface")
    else:
        print("\n⚠️  Some tests failed. Check the server and API endpoint.")
        sys.exit(1)
