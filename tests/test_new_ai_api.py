#!/usr/bin/env python3
"""
Test the updated AI generation API with multiple providers
"""
import asyncio
import aiohttp
import json

async def test_ai_generation_api():
    """Test the new AI generation API endpoints"""
    base_url = "http://127.0.0.1:8088"
    
    print("🧪 Testing AI Generation API with Multiple Providers")
    print("=" * 60)
    
    async with aiohttp.ClientSession() as session:
        # Test 1: List providers
        print("\n1️⃣ Testing /providers endpoint...")
        try:
            async with session.get(f"{base_url}/api/v1/ai/providers") as response:
                if response.status == 200:
                    data = await response.json()
                    print(f"✅ Found {len(data['providers'])} providers:")
                    for provider in data['providers']:
                        print(f"   - {provider['id']}: {provider['name']} (configured: {provider['configured']}, available: {provider['available']})")
                else:
                    print(f"❌ Provider list failed: {response.status}")
                    return False
        except Exception as e:
            print(f"❌ Provider list error: {e}")
            return False
        
        # Test 2: Get recommended provider
        print("\n2️⃣ Testing /providers/recommended endpoint...")
        try:
            async with session.get(f"{base_url}/api/v1/ai/providers/recommended") as response:
                if response.status == 200:
                    data = await response.json()
                    print(f"✅ Recommended provider: {data['recommended_provider']}")
                    print(f"   Model: {data['provider_info']['model']}")
                    print(f"   Max variations: {data['provider_info']['max_variations']}")
                else:
                    print(f"❌ Recommended provider failed: {response.status}")
        except Exception as e:
            print(f"❌ Recommended provider error: {e}")
        
        # Test 3: Generate single image
        print("\n3️⃣ Testing single image generation...")
        single_request = {
            "prompt": "A modern office building with solar panels",
            "ai_provider": "free-test-provider",
            "size": "1024x1024",
            "variations": 1
        }
        
        try:
            async with session.post(
                f"{base_url}/api/v1/ai/generate-image",
                json=single_request
            ) as response:
                if response.status == 200:
                    data = await response.json()
                    print(f"✅ Generated {len(data['images'])} image(s)")
                    print(f"   Provider: {data['provider']}")
                    print(f"   Model: {data['model']}")
                    print(f"   Cost: ${data.get('cost', 0)}")
                    print(f"   Image type: {data['metadata'].get('type', 'unknown')}")
                else:
                    error_text = await response.text()
                    print(f"❌ Single image generation failed: {response.status}")
                    print(f"   Error: {error_text}")
        except Exception as e:
            print(f"❌ Single image generation error: {e}")
        
        # Test 4: Generate multiple images
        print("\n4️⃣ Testing multiple image generation...")
        multi_request = {
            "prompt": "Sustainable technology products",
            "ai_provider": "free-test-provider",
            "size": "512x512",
            "variations": 3
        }
        
        try:
            async with session.post(
                f"{base_url}/api/v1/ai/generate-image",
                json=multi_request
            ) as response:
                if response.status == 200:
                    data = await response.json()
                    print(f"✅ Generated {len(data['images'])} image variations")
                    print(f"   Provider: {data['provider']}")
                    print(f"   Total cost: ${data.get('cost', 0)}")
                    for i, image_url in enumerate(data['images']):
                        print(f"   Image {i+1}: {image_url[:80]}...")
                else:
                    error_text = await response.text()
                    print(f"❌ Multi-image generation failed: {response.status}")
                    print(f"   Error: {error_text}")
        except Exception as e:
            print(f"❌ Multi-image generation error: {e}")
        
        # Test 5: Test backward compatibility endpoint
        print("\n5️⃣ Testing backward compatibility endpoint...")
        try:
            params = {
                "prompt": "Clean energy solutions",
                "ai_provider": "free-test-provider",
                "size": "1024x1024",
                "variations": 2
            }
            
            async with session.post(
                f"{base_url}/api/v1/ai/generate-image-multi",
                params=params
            ) as response:
                if response.status == 200:
                    data = await response.json()
                    print(f"✅ Backward compatibility works: {len(data['images'])} images")
                else:
                    print(f"❌ Backward compatibility failed: {response.status}")
        except Exception as e:
            print(f"❌ Backward compatibility error: {e}")
    
    print("\n🎉 API testing complete!")
    return True

if __name__ == "__main__":
    asyncio.run(test_ai_generation_api())
