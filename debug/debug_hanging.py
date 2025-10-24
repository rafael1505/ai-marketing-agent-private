#!/usr/bin/env python3
"""
Debug script to diagnose the hanging FormData authentication issue
"""

import asyncio
import aiohttp
import json
import time
from pathlib import Path

# Test configuration
BASE_URL = "http://127.0.0.1:8088"
LOGIN_URL = f"{BASE_URL}/api/v1/auth/login"
COMPANY_UPDATE_URL = f"{BASE_URL}/api/v1/companies/1"

async def test_login():
    """Test basic login functionality"""
    print("=== Testing Login ===")
    
    login_data = {
        "username": "test@example.com",
        "password": "password"
    }
    
    async with aiohttp.ClientSession() as session:
        try:
            async with session.post(LOGIN_URL, data=login_data, timeout=5) as response:
                if response.status == 200:
                    data = await response.json()
                    token = data.get("access_token")
                    print(f"✅ Login successful, token: {token[:20]}...")
                    return token
                else:
                    print(f"❌ Login failed: {response.status}")
                    text = await response.text()
                    print(f"Response: {text}")
                    return None
        except asyncio.TimeoutError:
            print("❌ Login timed out")
            return None
        except Exception as e:
            print(f"❌ Login error: {e}")
            return None

async def test_formdata_with_timeout(token, timeout_seconds=10):
    """Test FormData upload with timeout to see if it hangs"""
    print(f"=== Testing FormData Upload (timeout: {timeout_seconds}s) ===")
    
    headers = {
        "Authorization": f"Bearer {token}"
    }
    
    # Create a simple test file
    test_file_content = b"Test logo content"
    
    # Prepare FormData
    form_data = aiohttp.FormData()
    form_data.add_field('name', 'Updated Company Name')
    form_data.add_field('logo', test_file_content, filename='test_logo.png', content_type='image/png')
    
    async with aiohttp.ClientSession() as session:
        try:
            print(f"Starting FormData request at {time.strftime('%H:%M:%S')}")
            start_time = time.time()
            
            async with session.put(
                COMPANY_UPDATE_URL, 
                data=form_data, 
                headers=headers,
                timeout=aiohttp.ClientTimeout(total=timeout_seconds)
            ) as response:
                elapsed = time.time() - start_time
                print(f"✅ FormData request completed in {elapsed:.2f}s")
                print(f"Status: {response.status}")
                
                if response.status in [200, 422]:  # 422 might be validation error, but not hanging
                    try:
                        data = await response.json()
                        print(f"Response: {json.dumps(data, indent=2)}")
                    except:
                        text = await response.text()
                        print(f"Response text: {text}")
                else:
                    text = await response.text()
                    print(f"Error response: {text}")
                
                return True
                
        except asyncio.TimeoutError:
            elapsed = time.time() - start_time
            print(f"❌ FormData request TIMED OUT after {elapsed:.2f}s")
            return False
        except Exception as e:
            elapsed = time.time() - start_time
            print(f"❌ FormData request error after {elapsed:.2f}s: {e}")
            return False

async def main():
    print("Starting FormData hanging diagnosis...")
    print(f"Target: {BASE_URL}")
    
    # Test basic connectivity
    try:
        async with aiohttp.ClientSession() as session:
            async with session.get(f"{BASE_URL}/health", timeout=5) as response:
                if response.status == 200:
                    print("✅ API server is responding")
                else:
                    print(f"⚠️ API server responded with status {response.status}")
    except Exception as e:
        print(f"❌ Cannot connect to API server: {e}")
        return
    
    # Test login
    token = await test_login()
    if not token:
        print("Cannot proceed without valid token")
        return
    
    # Test FormData with progressively longer timeouts
    for timeout in [5, 10, 15]:
        print(f"\n--- Testing with {timeout}s timeout ---")
        success = await test_formdata_with_timeout(token, timeout)
        if success:
            print("✅ FormData request succeeded")
            break
        else:
            print(f"❌ FormData request failed with {timeout}s timeout")
    
    print("\nDiagnosis complete.")

if __name__ == "__main__":
    asyncio.run(main())
