#!/usr/bin/env python3

"""
Comprehensive test script for verifying all FormData submission cases.
Tests all the cases from the auth-debug-suite.html FormData Tests tab.
"""

import requests
import json
import logging
import sys
import time

# Set up logging
logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(levelname)s - %(message)s')
logger = logging.getLogger(__name__)

# Configuration
API_BASE_URL = "http://localhost:8088"
COMPANY_ID = "test_company"

# Test token - should match the one used in the auth-debug-suite.html
# This is a dummy token for testing purposes
TEST_TOKEN = "eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9.eyJzdWIiOiJ0ZXN0QGV4YW1wbGUuY29tIiwiZXhwIjoxNjUwMDAwMDAwfQ.1exampledevsignature"

def test_standard_formdata():
    """Test standard FormData submission (equivalent to "Submit FormData" button)"""
    logger.info("Testing standard FormData submission...")
    
    # Create FormData
    data = {
        "name": "Standard FormData Test",
        "description": "Testing standard FormData submission",
        "brand_colors": json.dumps(["#FF5733", "#33FF57"])  # Send as JSON string
    }
    
    headers = {
        "Authorization": f"Bearer {TEST_TOKEN}"
        # No Content-Type - let browser set it automatically
    }
    
    try:
        response = requests.put(
            f"{API_BASE_URL}/api/v1/companies/{COMPANY_ID}",
            headers=headers,
            data=data  # Use data parameter for FormData
        )
        
        logger.info(f"Status Code: {response.status_code}")
        logger.info(f"Headers: {dict(response.headers)}")
        logger.info(f"Response Content: {response.text}")
        
        if response.status_code == 200:
            logger.info("✅ TEST PASSED: Standard FormData submission")
            return True
        else:
            logger.error(f"❌ TEST FAILED: Standard FormData submission failed with status {response.status_code}")
            return False
    except Exception as e:
        logger.error(f"❌ TEST FAILED: {str(e)}")
        return False

def test_json_fallback():
    """Test JSON fallback (equivalent to "JSON Fallback" button)"""
    logger.info("Testing JSON fallback...")
    
    # JSON data
    data = {
        "name": "JSON Fallback Test",
        "description": "Testing JSON fallback",
        "brand_colors": ["#FF5733", "#33FF57"]
    }
    
    headers = {
        "Authorization": f"Bearer {TEST_TOKEN}",
        "Content-Type": "application/json"
    }
    
    try:
        response = requests.put(
            f"{API_BASE_URL}/api/v1/companies/{COMPANY_ID}",
            headers=headers,
            json=data
        )
        
        logger.info(f"Status Code: {response.status_code}")
        logger.info(f"Headers: {dict(response.headers)}")
        logger.info(f"Response Content: {response.text}")
        
        if response.status_code == 200:
            logger.info("✅ TEST PASSED: JSON fallback")
            return True
        else:
            logger.error(f"❌ TEST FAILED: JSON fallback failed with status {response.status_code}")
            return False
    except Exception as e:
        logger.error(f"❌ TEST FAILED: {str(e)}")
        return False

def test_auto_content_type():
    """Test with auto Content-Type (equivalent to "Auto (No Content-Type)" button)"""
    logger.info("Testing auto Content-Type...")
    
    # Create FormData
    data = {
        "name": "Auto Content-Type Test",
        "description": "Testing with auto Content-Type",
        "brand_colors": json.dumps(["#FF5733", "#33FF57"])
    }
    
    headers = {
        "Authorization": f"Bearer {TEST_TOKEN}"
        # No Content-Type - let browser/client set it
    }
    
    try:
        response = requests.put(
            f"{API_BASE_URL}/api/v1/companies/{COMPANY_ID}",
            headers=headers,
            data=data
        )
        
        logger.info(f"Status Code: {response.status_code}")
        logger.info(f"Headers: {dict(response.headers)}")
        logger.info(f"Response Content: {response.text}")
        
        if response.status_code == 200:
            logger.info("✅ TEST PASSED: Auto Content-Type")
            return True
        else:
            logger.error(f"❌ TEST FAILED: Auto Content-Type failed with status {response.status_code}")
            return False
    except Exception as e:
        logger.error(f"❌ TEST FAILED: {str(e)}")
        return False

def test_application_json():
    """Test with application/json Content-Type (equivalent to "application/json (correct)" button)"""
    logger.info("Testing application/json Content-Type...")
    
    # JSON data
    data = {
        "name": "Application JSON Test",
        "description": "Testing with application/json Content-Type",
        "brand_colors": ["#FF5733", "#33FF57"]
    }
    
    headers = {
        "Authorization": f"Bearer {TEST_TOKEN}",
        "Content-Type": "application/json"
    }
    
    try:
        response = requests.put(
            f"{API_BASE_URL}/api/v1/companies/{COMPANY_ID}",
            headers=headers,
            json=data
        )
        
        logger.info(f"Status Code: {response.status_code}")
        logger.info(f"Headers: {dict(response.headers)}")
        logger.info(f"Response Content: {response.text}")
        
        if response.status_code == 200:
            logger.info("✅ TEST PASSED: application/json Content-Type")
            return True
        else:
            logger.error(f"❌ TEST FAILED: application/json Content-Type failed with status {response.status_code}")
            return False
    except Exception as e:
        logger.error(f"❌ TEST FAILED: {str(e)}")
        return False

def test_multipart_form_data():
    """Test with multipart/form-data Content-Type without boundary (equivalent to "multipart/form-data" button)"""
    logger.info("Testing multipart/form-data Content-Type without boundary...")
    
    # JSON data
    data = {
        "name": "Multipart FormData Test",
        "description": "Testing with multipart/form-data Content-Type without boundary",
        "brand_colors": ["#FF5733", "#33FF57"]
    }
    
    headers = {
        "Authorization": f"Bearer {TEST_TOKEN}",
        "Content-Type": "multipart/form-data"  # No boundary parameter
    }
    
    try:
        response = requests.put(
            f"{API_BASE_URL}/api/v1/companies/{COMPANY_ID}",
            headers=headers,
            json=data  # Using json here forces it to send as JSON despite the Content-Type
        )
        
        logger.info(f"Status Code: {response.status_code}")
        logger.info(f"Headers: {dict(response.headers)}")
        logger.info(f"Response Content: {response.text}")
        
        if response.status_code == 200:
            logger.info("✅ TEST PASSED: multipart/form-data Content-Type without boundary")
            return True
        else:
            logger.error(f"❌ TEST FAILED: multipart/form-data Content-Type without boundary failed with status {response.status_code}")
            return False
    except Exception as e:
        logger.error(f"❌ TEST FAILED: {str(e)}")
        return False

def main():
    """Run all FormData tests."""
    logger.info("===== STARTING COMPREHENSIVE FORMDATA TESTS =====")
    
    # Wait for API server to be ready
    logger.info("Waiting for API server to be ready...")
    time.sleep(3)
    
    # Run all tests
    results = {
        "standard_formdata": test_standard_formdata(),
        "json_fallback": test_json_fallback(),
        "auto_content_type": test_auto_content_type(),
        "application_json": test_application_json(),
        "multipart_form_data": test_multipart_form_data()
    }
    
    # Summary
    logger.info("\n===== TEST SUMMARY =====")
    all_passed = True
    for test_name, result in results.items():
        logger.info(f"{test_name}: {'PASSED' if result else 'FAILED'}")
        if not result:
            all_passed = False
    
    if all_passed:
        logger.info("\n🎉 ALL TESTS PASSED! All FormData submission methods are working correctly!")
        return 0
    else:
        logger.error("\n❌ SOME TESTS FAILED. Please check the logs for details.")
        return 1

if __name__ == "__main__":
    sys.exit(main())
