#!/usr/bin/env python3
"""
Comprehensive test script to verify the Login functionality works properly,
while ensuring all other features in auth-debug-suite.html continue to work.
"""

import requests
import json
import logging
from time import sleep

# Set up logging
logging.basicConfig(level=logging.INFO, 
                   format='%(asctime)s - %(name)s - %(levelname)s - %(message)s')
logger = logging.getLogger(__name__)

# API URL
API_URL = "http://localhost:8088"

def test_login():
    """Test the login endpoint with the auth-debug-suite test credentials"""
    endpoint = f"{API_URL}/api/v1/auth/token"
    
    # Form data for login
    data = {
        "username": "test@example.com",
        "password": "testpassword"
    }
    
    logger.info(f"Testing login at {endpoint}")
    
    try:
        response = requests.post(
            endpoint,
            data=data,
            headers={"Content-Type": "application/x-www-form-urlencoded"}
        )
        
        logger.info(f"Status code: {response.status_code}")
        
        if response.status_code == 200:
            response_data = response.json()
            logger.info("Login successful!")
            logger.info(f"Token: {response_data['access_token'][:15]}...")
            return True, response_data.get("access_token")
        else:
            try:
                error_data = response.json()
                logger.error(f"Login failed with error: {json.dumps(error_data, indent=2)}")
            except:
                logger.error(f"Login failed with status {response.status_code}: {response.text}")
            return False, None
    except Exception as e:
        logger.error(f"Exception during login test: {str(e)}")
        return False, None

def verify_token(token):
    """Test the token verification endpoint with the obtained token"""
    endpoint = f"{API_URL}/api/v1/auth/verify"
    
    logger.info(f"Verifying token at {endpoint}")
    
    try:
        response = requests.get(
            endpoint,
            headers={"Authorization": f"Bearer {token}"}
        )
        
        logger.info(f"Status code: {response.status_code}")
        
        if response.status_code == 200:
            response_data = response.json()
            logger.info("Token verification successful!")
            logger.info(f"Response: {json.dumps(response_data, indent=2)}")
            return True
        else:
            logger.error(f"Token verification failed with status {response.status_code}: {response.text}")
            return False
    except Exception as e:
        logger.error(f"Exception during token verification: {str(e)}")
        return False

def get_company(token, company_id="test_company"):
    """Test getting a company using the token"""
    endpoint = f"{API_URL}/api/v1/companies/{company_id}"
    
    logger.info(f"Getting company from {endpoint}")
    
    try:
        response = requests.get(
            endpoint,
            headers={"Authorization": f"Bearer {token}"}
        )
        
        logger.info(f"Status code: {response.status_code}")
        
        if response.status_code == 200:
            response_data = response.json()
            logger.info("Get company successful!")
            logger.info(f"Company name: {response_data.get('name')}")
            return True
        else:
            logger.error(f"Get company failed with status {response.status_code}: {response.text}")
            return False
    except Exception as e:
        logger.error(f"Exception during get company: {str(e)}")
        return False

def test_formdata_submission(token, company_id="test_company"):
    """Test FormData submission to ensure it still works"""
    endpoint = f"{API_URL}/api/v1/companies/{company_id}"
    
    # Create form data with brand_colors
    data = {
        "name": "Updated via Test Script",
        "description": "This is a test update via FormData",
        "brand_colors": json.dumps(["#3B82F6", "#93C5FD"])
    }
    
    logger.info(f"Testing FormData submission to {endpoint}")
    
    try:
        response = requests.put(
            endpoint,
            data=data,  # Will be sent as multipart/form-data
            headers={"Authorization": f"Bearer {token}"}
        )
        
        logger.info(f"Status code: {response.status_code}")
        
        if response.status_code == 200:
            response_data = response.json()
            logger.info("FormData submission successful!")
            logger.info(f"Updated company name: {response_data.get('name')}")
            return True
        else:
            logger.error(f"FormData submission failed with status {response.status_code}: {response.text}")
            return False
    except Exception as e:
        logger.error(f"Exception during FormData submission: {str(e)}")
        return False

def test_post_method(token, company_id="test_company"):
    """Test POST method to ensure it still works"""
    endpoint = f"{API_URL}/api/v1/companies/{company_id}"
    
    data = {
        "name": "Updated via POST Method",
        "description": "This is a test using POST method",
        "brand_colors": ["#3B82F6", "#93C5FD"]
    }
    
    logger.info(f"Testing POST method to {endpoint}")
    
    try:
        response = requests.post(
            endpoint,
            json=data,
            headers={
                "Authorization": f"Bearer {token}",
                "Content-Type": "application/json"
            }
        )
        
        logger.info(f"Status code: {response.status_code}")
        
        if response.status_code == 200:
            response_data = response.json()
            logger.info("POST method successful!")
            logger.info(f"Updated company name: {response_data.get('name')}")
            return True
        else:
            logger.error(f"POST method failed with status {response.status_code}: {response.text}")
            return False
    except Exception as e:
        logger.error(f"Exception during POST method test: {str(e)}")
        return False

def run_all_tests():
    """Run all tests in sequence"""
    results = {}
    
    # Test 1: Login
    logger.info("=== TEST 1: LOGIN ===")
    login_success, token = test_login()
    results["login"] = login_success
    
    if not login_success:
        logger.error("Login failed, cannot continue with other tests")
        return results
    
    # A short pause between tests
    sleep(1)
    
    # Test 2: Verify Token
    logger.info("\n=== TEST 2: VERIFY TOKEN ===")
    verify_success = verify_token(token)
    results["verify_token"] = verify_success
    
    # A short pause between tests
    sleep(1)
    
    # Test 3: Get Company
    logger.info("\n=== TEST 3: GET COMPANY ===")
    get_company_success = get_company(token)
    results["get_company"] = get_company_success
    
    # A short pause between tests
    sleep(1)
    
    # Test 4: FormData Submission
    logger.info("\n=== TEST 4: FORMDATA SUBMISSION ===")
    formdata_success = test_formdata_submission(token)
    results["formdata_submission"] = formdata_success
    
    # A short pause between tests
    sleep(1)
    
    # Test 5: POST Method
    logger.info("\n=== TEST 5: POST METHOD ===")
    post_success = test_post_method(token)
    results["post_method"] = post_success
    
    return results

if __name__ == "__main__":
    logger.info("Starting comprehensive test suite")
    results = run_all_tests()
    
    # Print summary
    print("\n=== TEST RESULTS SUMMARY ===")
    all_passed = True
    for test, result in results.items():
        status = "✅ PASS" if result else "❌ FAIL"
        if not result:
            all_passed = False
        print(f"{status} - {test}")
    
    if all_passed:
        print("\n🎉 ALL TESTS PASSED! The login fix is working and all other features are intact.")
    else:
        print("\n⚠️ Some tests failed. Please review the logs above for details.")
