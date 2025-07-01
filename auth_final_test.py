#!/usr/bin/env python3
"""
Final fix for auth-debug-suite Login Test
This script ensures the Login Test works by testing both direct and proxy auth paths
"""
import requests
import json
import logging
import sys

# Configure logging
logging.basicConfig(level=logging.INFO, 
                   format='%(asctime)s - %(name)s - %(levelname)s - %(message)s')
logger = logging.getLogger(__name__)

def test_full_auth_flow():
    # First, test direct API endpoint
    logger.info("Testing direct API login...")
    try:
        direct_response = requests.post(
            "http://127.0.0.1:8088/api/v1/auth/token",
            data={
                "username": "test@example.com",
                "password": "testpassword"
            },
            headers={"Content-Type": "application/x-www-form-urlencoded"}
        )
        
        logger.info(f"Direct API status: {direct_response.status_code}")
        if direct_response.status_code == 200:
            logger.info("✅ Direct API login successful!")
            direct_token = direct_response.json().get("access_token", "")[:20] + "..."
            logger.info(f"Direct token: {direct_token}")
        else:
            logger.error(f"❌ Direct API login failed: {direct_response.text}")
            return False
    except Exception as e:
        logger.exception(f"Error testing direct API: {str(e)}")
        return False
    
    # Then test the proxy endpoint that's used by auth-debug-suite.html
    logger.info("Testing proxy API login...")
    try:
        proxy_response = requests.post(
            "http://127.0.0.1:3001/auth-proxy/token",
            data={
                "username": "test@example.com",
                "password": "testpassword"
            },
            headers={"Content-Type": "application/x-www-form-urlencoded"}
        )
        
        logger.info(f"Proxy API status: {proxy_response.status_code}")
        if proxy_response.status_code == 200:
            logger.info("✅ Proxy API login successful!")
            proxy_token = proxy_response.json().get("access_token", "")[:20] + "..."
            logger.info(f"Proxy token: {proxy_token}")
        else:
            logger.error(f"❌ Proxy API login failed: {proxy_response.text}")
            return False
    except Exception as e:
        logger.exception(f"Error testing proxy API: {str(e)}")
        return False
    
    logger.info("🎉 BOTH AUTH FLOWS ARE WORKING! Auth-debug-suite.html should now work.")
    return True

if __name__ == "__main__":
    if test_full_auth_flow():
        sys.exit(0)
    else:
        sys.exit(1)
