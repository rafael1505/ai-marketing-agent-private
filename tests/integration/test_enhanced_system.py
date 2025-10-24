#!/usr/bin/env python3
"""
Test the enhanced error handling system end-to-end
"""
import sys
sys.path.insert(0, '.')

import requests
import json

def test_enhanced_error_handling():
    """Test the enhanced error handling system."""
    print("🧪 Testing Enhanced Error Handling System")
    print("=" * 50)
    
    # Test the API directly
    try:
        response = requests.post(
            "http://127.0.0.1:8088/api/generate-content",
            json={"provider": "openai", "text_prompt": "test"},
            timeout=10
        )
        
        print(f"📊 Response Status: {response.status_code}")
        print(f"📄 Response Text: {response.text[:500]}")
        
        if response.status_code == 200:
            data = response.json()
            if "error" in data:
                error = data["error"]
                print("\n✅ Enhanced Error Response Received!")
                print(f"🔍 Error Type: {error.get('type', 'N/A')}")
                print(f"💬 User Message: {error.get('user_message', 'N/A')}")
                print(f"🔧 Suggested Actions: {error.get('suggested_actions', 'N/A')}")
                print(f"🆔 Correlation ID: {error.get('correlation_id', 'N/A')}")
                
                # Test Portuguese-ready structure
                if error.get('type') == 'BILLING_LIMIT_REACHED':
                    print("\n🇵🇹 Portuguese Translation Ready:")
                    print("   Message Key: billing_limit_reached")
                    print("   Expected PT: 'O limite de faturamento da sua conta OpenAI foi atingido'")
                    return True
            else:
                print("❌ No error in successful response - this shouldn't happen in our test")
                return False
        else:
            print(f"❌ API returned error status: {response.status_code}")
            return False
            
    except Exception as e:
        print(f"❌ Test failed with exception: {e}")
        return False

def test_frontend_integration():
    """Test if frontend is accessible for integration."""
    print("\n🌐 Testing Frontend Integration")
    print("=" * 50)
    
    try:
        response = requests.get("http://127.0.0.1:3001", timeout=5)
        if response.status_code == 200:
            print("✅ Frontend is accessible at http://127.0.0.1:3001")
            print("🔗 Ready for error handling integration testing")
            return True
        else:
            print(f"❌ Frontend returned status: {response.status_code}")
            return False
    except Exception as e:
        print(f"❌ Frontend not accessible: {e}")
        return False

def check_api_status():
    """Check if API is running and healthy."""
    print("🏥 Checking API Health")
    print("=" * 50)
    
    try:
        response = requests.get("http://127.0.0.1:8088/api/health", timeout=5)
        if response.status_code == 200:
            data = response.json()
            print("✅ API is healthy and running")
            print(f"📋 Status: {data.get('status', 'unknown')}")
            print(f"🔧 Enhanced Errors: {data.get('enhanced_errors', False)}")
            return True
        else:
            print(f"❌ API health check failed: {response.status_code}")
            return False
    except Exception as e:
        print(f"❌ API not responding: {e}")
        return False

if __name__ == "__main__":
    print("🚀 AI Marketing Agent - Enhanced Error Handling Test Suite")
    print("=" * 60)
    
    # Run all tests
    api_healthy = check_api_status()
    frontend_ready = test_frontend_integration()
    error_handling_works = test_enhanced_error_handling() if api_healthy else False
    
    print("\n📊 Test Results Summary")
    print("=" * 60)
    print(f"🏥 API Health: {'✅ PASS' if api_healthy else '❌ FAIL'}")
    print(f"🌐 Frontend Ready: {'✅ PASS' if frontend_ready else '❌ FAIL'}")
    print(f"🔧 Enhanced Errors: {'✅ PASS' if error_handling_works else '❌ FAIL'}")
    
    if api_healthy and frontend_ready and error_handling_works:
        print("\n🎉 ALL TESTS PASSED!")
        print("🔗 System ready for end-to-end Portuguese error testing")
        print("📝 Next step: Test error flow in actual frontend application")
    else:
        print("\n⚠️  Some tests failed - check the issues above")
    
    print(f"\n🌍 Access Points:")
    print(f"   • Frontend: http://127.0.0.1:3001")
    print(f"   • API Docs: http://127.0.0.1:8088/docs")
    print(f"   • API Health: http://127.0.0.1:8088/api/health")