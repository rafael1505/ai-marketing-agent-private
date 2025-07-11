#!/usr/bin/env python3
"""
Test Pollinations.ai API for free image generation
"""
import requests
import urllib.parse

def test_pollinations():
    """Test the Pollinations.ai free image generation API"""
    
    print("🧪 Testing Pollinations.ai Free Image Generation")
    print("=" * 60)
    
    test_prompts = [
        "a modern technology product with blue and silver colors",
        "professional business meeting in modern office",
        "creative marketing design with vibrant colors",
        "healthcare technology with clean white and blue design"
    ]
    
    for i, prompt in enumerate(test_prompts, 1):
        print(f"\n{i}. Testing prompt: '{prompt}'")
        
        # URL encode the prompt
        encoded_prompt = urllib.parse.quote(prompt)
        url = f"https://image.pollinations.ai/prompt/{encoded_prompt}"
        
        print(f"   URL: {url}")
        
        try:
            response = requests.get(url, timeout=30)
            print(f"   Status: {response.status_code}")
            print(f"   Content-Type: {response.headers.get('content-type', 'unknown')}")
            print(f"   Content-Length: {len(response.content)} bytes")
            
            if response.status_code == 200 and 'image' in response.headers.get('content-type', ''):
                print("   ✅ Successfully generated image!")
            else:
                print("   ❌ Failed to generate image")
                print(f"   Response: {response.text[:200]}")
                
        except requests.exceptions.Timeout:
            print("   ⏰ Request timed out (30s)")
        except Exception as e:
            print(f"   ❌ Error: {e}")
    
    print("\n" + "=" * 60)
    print("📊 Test Summary:")
    print("Pollinations.ai provides free AI image generation without API keys")
    print("Images are returned as direct binary data (JPEG/PNG)")
    print("Suitable for development and testing purposes")

if __name__ == "__main__":
    test_pollinations()
