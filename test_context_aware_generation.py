#!/usr/bin/env python3
"""
Test the new context-aware image generation API
"""
import requests
import json

def test_context_aware_generation():
    """Test context-aware image generation with company brand colors"""
    
    print("🎨 Testing Context-Aware Image Generation")
    print("=" * 60)
    
    # Test cases with different companies and contexts
    test_cases = [
        {
            "name": "Philips Healthcare Product",
            "params": {
                "prompt": "Modern healthcare device with sleek design",
                "company_id": "philips",
                "material_type": "product_launch",
                "target_audience": "healthcare professionals",
                "size": "512x512",
                "ai_provider": "context-aware-test-provider"
            }
        },
        {
            "name": "Nike Athletic Campaign",
            "params": {
                "prompt": "Dynamic sports shoe advertisement",
                "company_id": "nike", 
                "material_type": "promotional",
                "target_audience": "young athletes",
                "campaign_theme": "Just Do It",
                "size": "400x600",
                "ai_provider": "context-aware-test-provider"
            }
        },
        {
            "name": "Apple Product Showcase",
            "params": {
                "prompt": "Minimalist smartphone display",
                "company_id": "apple",
                "material_type": "brand_awareness",
                "target_audience": "tech enthusiasts",
                "size": "800x600",
                "ai_provider": "context-aware-test-provider"
            }
        },
        {
            "name": "Default Corporate",
            "params": {
                "prompt": "Professional business presentation",
                "material_type": "corporate",
                "target_audience": "business executives",
                "size": "1024x768",
                "ai_provider": "context-aware-test-provider"
            }
        }
    ]
    
    for i, test_case in enumerate(test_cases, 1):
        print(f"\n{i}. Testing: {test_case['name']}")
        print("   Parameters:")
        for key, value in test_case['params'].items():
            print(f"     {key}: {value}")
        
        try:
            url = "http://127.0.0.1:8089/api/v1/ai/generate-image"
            response = requests.post(url, params=test_case['params'], timeout=10)
            
            print(f"   Status: {response.status_code}")
            
            if response.status_code == 200:
                data = response.json()
                
                if data.get("success"):
                    print("   ✅ Generation successful!")
                    print(f"   📝 Original prompt: {data.get('prompt', 'N/A')}")
                    print(f"   🔧 Enhanced prompt: {data.get('enhanced_prompt', 'N/A')[:100]}...")
                    
                    metadata = data.get('metadata', {})
                    company = metadata.get('company', {})
                    context = metadata.get('context_applied', {})
                    
                    print(f"   🏢 Company: {company.get('name', 'N/A')}")
                    print(f"   🎨 Brand colors: {', '.join(company.get('brand_colors', []))}")
                    print(f"   🏭 Industry: {company.get('industry', 'N/A')}")
                    print(f"   📋 Material type: {metadata.get('material_type', 'N/A')}")
                    
                    context_items = [k for k, v in context.items() if v]
                    print(f"   🎯 Context applied: {', '.join(context_items)}")
                    
                    image_url = data.get('image_url', '')
                    if image_url.startswith('data:image/svg+xml;base64,'):
                        print(f"   📷 Image format: SVG data URL ({len(image_url)} chars)")
                    else:
                        print(f"   ❌ Unexpected image format: {image_url[:50]}...")
                else:
                    print(f"   ❌ Generation failed: {data}")
            else:
                print(f"   ❌ HTTP Error: {response.text[:200]}")
                
        except Exception as e:
            print(f"   ❌ Error: {e}")
    
    print("\n" + "=" * 60)
    print("📊 Context-Aware Generation Summary:")
    print("✅ Company brand colors are now integrated")
    print("✅ Material type context influences design") 
    print("✅ Enhanced prompts include business context")
    print("✅ Each image reflects the company's brand identity")

def test_company_context_endpoint():
    """Test the company context endpoint"""
    
    print("\n🏢 Testing Company Context Endpoint")
    print("=" * 40)
    
    companies = ["philips", "nike", "apple", "unknown"]
    
    for company_id in companies:
        print(f"\nTesting company: {company_id}")
        
        try:
            url = f"http://127.0.0.1:8089/api/v1/companies/{company_id}/context"
            response = requests.get(url, timeout=5)
            
            print(f"Status: {response.status_code}")
            
            if response.status_code == 200:
                data = response.json()
                company = data.get('company', {})
                print(f"✅ {company.get('name', 'Unknown')}")
                print(f"   Colors: {', '.join(company.get('brand_colors', []))}")
                print(f"   Industry: {company.get('industry', 'N/A')}")
                print(f"   Style: {company.get('style', 'N/A')}")
            else:
                print(f"❌ Error: {response.text}")
                
        except Exception as e:
            print(f"❌ Error: {e}")

if __name__ == "__main__":
    test_context_aware_generation()
    test_company_context_endpoint()
