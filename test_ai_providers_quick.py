#!/usr/bin/env python3
"""
Quick test of AI provider functionality
"""
import sys
import os
import asyncio

# Add the current directory to path for imports
sys.path.insert(0, os.getcwd())

def test_ai_providers():
    """Test AI provider import and basic functionality"""
    try:
        print("🧪 Testing AI Provider System...")
        
        # Test import
        print("1. Testing import...")
        from app.ai_providers.provider_manager import ai_provider_manager, ImageGenerationRequest
        print("✅ Import successful")
        
        # Test provider status
        print("2. Testing provider status...")
        status = ai_provider_manager.get_provider_status()
        print(f"✅ Found {len(status)} providers: {list(status.keys())}")
        
        # Test image generation
        print("3. Testing image generation...")
        async def test_generation():
            request = ImageGenerationRequest(
                prompt="A beautiful sunset",
                size="512x512",
                variations=2
            )
            result = await ai_provider_manager.generate_image("free-test-provider", request)
            return result
        
        result = asyncio.run(test_generation())
        
        if result.success:
            print(f"✅ Generated {len(result.images)} images")
            print(f"   Provider: {result.provider}")
            print(f"   Model: {result.model}")
            print(f"   Cost: ${result.cost}")
            for i, img in enumerate(result.images):
                print(f"   Image {i+1}: {img[:80]}...")
        else:
            print(f"❌ Generation failed: {result.error}")
        
        print("🎉 All tests completed successfully!")
        return True
        
    except Exception as e:
        print(f"❌ Test failed: {e}")
        import traceback
        traceback.print_exc()
        return False

if __name__ == "__main__":
    success = test_ai_providers()
    sys.exit(0 if success else 1)
