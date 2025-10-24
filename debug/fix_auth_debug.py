#!/usr/bin/env python3
"""
Diagnostic script to debug auth endpoint issues in auth-debug-suite.html
"""
import requests
import json
import logging

# Configure logging
logging.basicConfig(level=logging.DEBUG, 
                   format='%(asctime)s - %(name)s - %(levelname)s - %(message)s')
logger = logging.getLogger(__name__)

def test_auth_direct():
    """
    Test the auth endpoint directly
    """
    try:
        logger.info("Testing authentication directly to the FastAPI endpoint")
        url = "http://127.0.0.1:8088/api/v1/auth/token"
        data = {
            "username": "test@example.com",
            "password": "testpassword"
        }
        
        # Use application/x-www-form-urlencoded content type
        headers = {"Content-Type": "application/x-www-form-urlencoded"}
        
        # Make the request with proxy bypass
        response = requests.post(url, 
                               data=data, 
                               headers=headers, 
                               proxies={"http": None, "https": None})
        
        logger.info(f"Response status: {response.status_code}")
        
        if response.status_code == 200:
            try:
                result = response.json()
                logger.info(f"Success! Received token: {result.get('access_token', '')[:20]}...")
                return result
            except json.JSONDecodeError:
                logger.error(f"Failed to parse JSON response: {response.text}")
                return None
        else:
            logger.error(f"Error response: {response.text}")
            return None
    except Exception as e:
        logger.exception(f"Exception during auth test: {str(e)}")
        return None

def test_auth_proxy():
    """
    Test the auth endpoint via Next.js proxy
    """
    try:
        logger.info("Testing authentication through Next.js auth-proxy")
        url = "http://127.0.0.1:3001/auth-proxy/token"
        data = {
            "username": "test@example.com",
            "password": "testpassword"
        }
        
        # Use application/x-www-form-urlencoded content type
        headers = {"Content-Type": "application/x-www-form-urlencoded"}
        
        # Make the request with proxy bypass
        response = requests.post(url, 
                               data=data, 
                               headers=headers, 
                               proxies={"http": None, "https": None})
        
        logger.info(f"Response status: {response.status_code}")
        
        if response.status_code == 200:
            try:
                result = response.json()
                logger.info(f"Success! Received token: {result.get('access_token', '')[:20]}...")
                return result
            except json.JSONDecodeError:
                logger.error(f"Failed to parse JSON response: {response.text}")
                return None
        else:
            logger.error(f"Error response: {response.text}")
            return None
    except Exception as e:
        logger.exception(f"Exception during auth proxy test: {str(e)}")
        return None

if __name__ == "__main__":
    print("Testing direct API auth endpoint...")
    result_direct = test_auth_direct()
    
    print("\nTesting Next.js proxy auth endpoint...")
    result_proxy = test_auth_proxy()
    
    # Save the token to a file for debugging
    if result_direct and "access_token" in result_direct:
        with open("auth_token.json", "w") as f:
            json.dump(result_direct, f, indent=2)
        print(f"\nToken saved to auth_token.json")
