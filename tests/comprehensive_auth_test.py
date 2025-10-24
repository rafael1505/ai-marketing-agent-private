#!/usr/bin/env python3
"""
Comprehensive authentication test script that tests both JSON and FormData requests
with authentication.
"""
import requests
import json
import time
from typing import Dict, Any, Optional
import logging

# Configure logging
logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(levelname)s - %(message)s')
logger = logging.getLogger(__name__)

# API Base URL
API_BASE_URL = "http://127.0.0.1:8088/api/v1"

def login(username: str, password: str) -> Optional[str]:
    """
    Attempt to login and get an auth token
    """
    logger.info(f"Attempting login with user: {username}")
    
    # Try both token endpoints
    endpoints = ["/auth/token", "/auth/login"]
    
    for endpoint in endpoints:
        login_url = f"{API_BASE_URL}{endpoint}"
        login_data = {
            "username": username,
            "password": password
        }
        
        try:
            logger.info(f"POST {login_url}")
            response = requests.post(login_url, data=login_data)
            logger.info(f"Status: {response.status_code}")
            
            if response.status_code == 200:
                logger.info("Login successful!")
                token_data = response.json()
                token = token_data.get('access_token')
                logger.info(f"Token: {token[:10]}...")
                return token
            else:
                logger.warning(f"Login failed on {endpoint}: {response.text}")
        except Exception as e:
            logger.error(f"Error on {endpoint}: {str(e)}")
    
    logger.error("All login attempts failed")
    return None

def test_json_request(token: str) -> bool:
    """
    Test a JSON request with authentication
    """
    logger.info("Testing JSON request with authentication")
    headers = {"Authorization": f"Bearer {token}"}
    
    companies_url = f"{API_BASE_URL}/companies/active"
    try:
        logger.info(f"GET {companies_url}")
        response = requests.get(companies_url, headers=headers)
        logger.info(f"Status: {response.status_code}")
        
        if response.status_code == 200:
            logger.info("JSON request successful!")
            return True
        else:
            logger.error(f"JSON request failed: {response.text}")
            return False
    except Exception as e:
        logger.error(f"Error during JSON request: {str(e)}")
        return False

def test_formdata_request(token: str) -> bool:
    """
    Test a FormData request with authentication
    """
    logger.info("Testing FormData request with authentication")
    headers = {"Authorization": f"Bearer {token}"}
    
    test_form_url = f"{API_BASE_URL}/auth-test/test-form"
    
    # Create a simple text file
    file_content = b"This is a test file for FormData authentication"
    files = {
        'test_file': ('test.txt', file_content, 'text/plain')
    }
    
    data = {
        'test_field': 'This is a test field value'
    }
    
    try:
        logger.info(f"POST {test_form_url} with FormData")
        response = requests.post(test_form_url, headers=headers, data=data, files=files)
        logger.info(f"Status: {response.status_code}")
        
        if response.status_code == 200:
            logger.info("FormData request successful!")
            result = response.json()
            logger.info(f"Response: {json.dumps(result, indent=2)}")
            return True
        else:
            logger.error(f"FormData request failed: {response.text}")
            return False
    except Exception as e:
        logger.error(f"Error during FormData request: {str(e)}")
        return False

def test_auth_debug(token: str) -> bool:
    """
    Test the auth debug endpoint
    """
    logger.info("Testing auth debug endpoint")
    headers = {"Authorization": f"Bearer {token}"}
    
    debug_url = f"{API_BASE_URL}/auth-test/auth-debug"
    
    try:
        logger.info(f"GET {debug_url}")
        response = requests.get(debug_url, headers=headers)
        logger.info(f"Status: {response.status_code}")
        
        if response.status_code == 200:
            logger.info("Auth debug request successful!")
            result = response.json()
            logger.info(f"Auth headers detected: {result.get('has_auth_header')}")
            logger.info(f"Auth header format: {result.get('auth_header_format')}")
            logger.info(f"Token length: {result.get('token_length')}")
            return True
        else:
            logger.error(f"Auth debug request failed: {response.text}")
            return False
    except Exception as e:
        logger.error(f"Error during auth debug request: {str(e)}")
        return False

def main() -> int:
    """
    Main test function
    """
    logger.info("Starting comprehensive authentication test")
    
    # Step 1: Wait for API server to be ready
    logger.info("Waiting for API server to be ready...")
    max_retries = 10
    retries = 0
    
    while retries < max_retries:
        try:
            health_response = requests.get(f"{API_BASE_URL}/diagnostic/health")
            if health_response.status_code == 200:
                logger.info("API server is ready!")
                break
        except Exception:
            pass
        
        retries += 1
        logger.info(f"API server not ready, retrying ({retries}/{max_retries})...")
        time.sleep(1)
    
    if retries >= max_retries:
        logger.error("API server failed to respond. Make sure it's running.")
        return 1
    
    # Step 2: Login to get token
    token = login("test@example.com", "testpassword")
    if not token:
        return 1
    
    # Step 3: Test JSON request with auth
    if not test_json_request(token):
        return 1
    
    # Step 4: Test FormData request with auth
    if not test_formdata_request(token):
        return 1
    
    # Step 5: Test auth debug endpoint
    if not test_auth_debug(token):
        return 1
    
    logger.info("=== All tests passed! Authentication fixes are working correctly! ===")
    return 0

if __name__ == "__main__":
    exit(main())
