#!/usr/bin/env python3
"""
Final verification showing the difference between basic and context-aware generation
"""
import requests
import json

def compare_providers():
    """Compare basic vs context-aware image generation"""
    
    print("🔍 Comparing Basic vs Context-Aware Image Generation")
    print("=" * 70)
    
    test_prompt = "Professional healthcare product marketing image"
    test_size = "512x512"
    
    # Test 1: Basic provider (random images)
    print("\n1️⃣  BASIC PROVIDER (Random Images)")
    print("-" * 40)
    
    try:
        url = "http://127.0.0.1:8089/api/v1/ai/generate-image"
        params = {
            "prompt": test_prompt,
            "ai_provider": "free-test-provider",
            "size": test_size
        }
        
        response = requests.post(url, params=params, timeout=10)
        
        if response.status_code == 200:
            data = response.json()
            print(f"✅ Status: {response.status_code}")
            print(f"📝 Prompt: {data.get('prompt')}")
            print(f"📷 Image URL: {data.get('image_url', '')[:80]}...")
            
            metadata = data.get('metadata', {})
            print(f"🔧 Service: {metadata.get('service', 'unknown')}")
            print(f"📊 Format: {metadata.get('format', 'unknown')}")
            print(f"🎯 Context Applied: None (random generation)")
        else:
            print(f"❌ Failed: {response.status_code}")
            
    except Exception as e:
        print(f"❌ Error: {e}")
    
    # Test 2: Context-aware provider with Philips branding
    print("\n2️⃣  CONTEXT-AWARE PROVIDER (Philips Healthcare)")
    print("-" * 50)
    
    try:
        params = {
            "prompt": test_prompt,
            "ai_provider": "context-aware-test-provider",
            "size": test_size,
            "company_id": "philips",
            "material_type": "product_launch",
            "target_audience": "healthcare professionals"
        }
        
        response = requests.post(url, params=params, timeout=10)
        
        if response.status_code == 200:
            data = response.json()
            print(f"✅ Status: {response.status_code}")
            print(f"📝 Original Prompt: {data.get('prompt')}")
            print(f"🔧 Enhanced Prompt: {data.get('enhanced_prompt', '')[:100]}...")
            print(f"📷 Image URL: {data.get('image_url', '')[:80]}...")
            
            metadata = data.get('metadata', {})
            company = metadata.get('company', {})
            context = metadata.get('context_applied', {})
            
            print(f"🏢 Company: {company.get('name')}")
            print(f"🎨 Brand Colors: {', '.join(company.get('brand_colors', []))}")
            print(f"🏭 Industry: {company.get('industry')}")
            print(f"📋 Material Type: {metadata.get('material_type')}")
            print(f"🎯 Context Applied:")
            for key, value in context.items():
                status = "✅" if value else "❌"
                print(f"   {status} {key.replace('_', ' ').title()}")
        else:
            print(f"❌ Failed: {response.status_code}")
            
    except Exception as e:
        print(f"❌ Error: {e}")
    
    # Test 3: Context-aware provider with Nike branding
    print("\n3️⃣  CONTEXT-AWARE PROVIDER (Nike Sports)")
    print("-" * 45)
    
    try:
        params = {
            "prompt": "Dynamic athletic shoe advertisement",
            "ai_provider": "context-aware-test-provider", 
            "size": test_size,
            "company_id": "nike",
            "material_type": "promotional",
            "target_audience": "young athletes",
            "campaign_theme": "Just Do It"
        }
        
        response = requests.post(url, params=params, timeout=10)
        
        if response.status_code == 200:
            data = response.json()
            print(f"✅ Status: {response.status_code}")
            print(f"📝 Original Prompt: {data.get('prompt')}")
            print(f"🔧 Enhanced Prompt: {data.get('enhanced_prompt', '')[:100]}...")
            
            metadata = data.get('metadata', {})
            company = metadata.get('company', {})
            
            print(f"🏢 Company: {company.get('name')}")
            print(f"🎨 Brand Colors: {', '.join(company.get('brand_colors', []))}")
            print(f"🏭 Industry: {company.get('industry')}")
            print(f"📋 Material Type: {metadata.get('material_type')}")
        else:
            print(f"❌ Failed: {response.status_code}")
            
    except Exception as e:
        print(f"❌ Error: {e}")
    
    print("\n" + "=" * 70)
    print("📊 COMPARISON SUMMARY")
    print("=" * 70)
    print("🔸 Basic Provider:")
    print("   • Generates random SVG patterns")
    print("   • No company context consideration") 
    print("   • No brand color integration")
    print("   • No material type awareness")
    print("   • Generic, one-size-fits-all output")
    
    print("\n🔸 Context-Aware Provider:")
    print("   • Uses company brand colors in design")
    print("   • Considers industry and company style")
    print("   • Integrates material type context")
    print("   • Enhances prompts with business context")
    print("   • Tailored output for specific use cases")
    
    print("\n🎯 KEY BENEFITS:")
    print("   ✅ Brand consistency across materials")
    print("   ✅ Industry-appropriate styling")
    print("   ✅ Context-driven image generation")
    print("   ✅ Professional marketing alignment")
    print("   ✅ Automated prompt enhancement")

def test_available_companies():
    """Test all available company contexts"""
    
    print("\n🏢 Available Company Contexts")
    print("=" * 40)
    
    companies = ["philips", "nike", "apple", "default"]
    
    for company_id in companies:
        try:
            if company_id == "default":
                url = f"http://127.0.0.1:8089/api/v1/companies/unknown/context"
            else:
                url = f"http://127.0.0.1:8089/api/v1/companies/{company_id}/context"
                
            response = requests.get(url, timeout=5)
            
            if response.status_code == 200:
                data = response.json()
                company = data.get('company', {})
                print(f"\n{company.get('name', 'Unknown')}:")
                print(f"   🎨 Colors: {', '.join(company.get('brand_colors', []))}")
                print(f"   🏭 Industry: {company.get('industry', 'N/A')}")
                print(f"   ✨ Style: {company.get('style', 'N/A')}")
            else:
                print(f"\n❌ {company_id}: Error {response.status_code}")
                
        except Exception as e:
            print(f"\n❌ {company_id}: {e}")

if __name__ == "__main__":
    compare_providers()
    test_available_companies()
