#!/usr/bin/env python3

"""
Test script to verify the POST method to /api/v1/companies/{company_id} works properly.
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

def test_post_company():
    """Test POST request to update a company."""
    logger.info("Testing POST request to update a company...")
    
    # Data to send
    data = {
        "name": "POST Method Test",
        "description": "This tests the POST endpoint for updating a company",
        "brand_colors": ["#AA00FF", "#00AAFF"]
    }
    
    headers = {
        "Content-Type": "application/json",
        "Authorization": f"Bearer {TEST_TOKEN}"
    }
    
    try:
        # Send the request
        response = requests.post(
            f"{API_BASE_URL}/api/v1/companies/{COMPANY_ID}",
            headers=headers,
            json=data
        )
        
        # Print detailed info
        logger.info(f"Status Code: {response.status_code}")
        logger.info(f"Headers: {dict(response.headers)}")
        logger.info(f"Response Content: {response.text}")
        
        # Check if successful
        if response.status_code == 200:
            logger.info("✅ TEST PASSED: POST request to update company is successful!")
            return True
        else:
            logger.error(f"❌ TEST FAILED: POST request failed with status {response.status_code}")
            return False
    except Exception as e:
        logger.error(f"❌ TEST FAILED: {str(e)}")
        return False

def test_put_company():
    """Test PUT request to update a company to verify it still works."""
    logger.info("Testing PUT request to update a company...")
    
    # Data to send
    data = {
        "name": "PUT Method Test",
        "description": "This tests the PUT endpoint for updating a company",
        "brand_colors": ["#FF00AA", "#FFAA00"]
    }
    
    headers = {
        "Content-Type": "application/json",
        "Authorization": f"Bearer {TEST_TOKEN}"
    }
    
    try:
        # Send the request
        response = requests.put(
            f"{API_BASE_URL}/api/v1/companies/{COMPANY_ID}",
            headers=headers,
            json=data
        )
        
        # Print detailed info
        logger.info(f"Status Code: {response.status_code}")
        logger.info(f"Headers: {dict(response.headers)}")
        logger.info(f"Response Content: {response.text}")
        
        # Check if successful
        if response.status_code == 200:
            logger.info("✅ TEST PASSED: PUT request to update company is successful!")
            return True
        else:
            logger.error(f"❌ TEST FAILED: PUT request failed with status {response.status_code}")
            return False
    except Exception as e:
        logger.error(f"❌ TEST FAILED: {str(e)}")
        return False

def test_get_company():
    """Test GET request to get a company to verify it still works."""
    logger.info("Testing GET request to retrieve a company...")
    
    headers = {
        "Authorization": f"Bearer {TEST_TOKEN}"
    }
    
    try:
        # Send the request
        response = requests.get(
            f"{API_BASE_URL}/api/v1/companies/{COMPANY_ID}",
            headers=headers
        )
        
        # Print detailed info
        logger.info(f"Status Code: {response.status_code}")
        logger.info(f"Headers: {dict(response.headers)}")
        logger.info(f"Response Content: {response.text}")
        
        # Check if successful
        if response.status_code == 200:
            logger.info("✅ TEST PASSED: GET request to retrieve company is successful!")
            return True
        else:
            logger.error(f"❌ TEST FAILED: GET request failed with status {response.status_code}")
            return False
    except Exception as e:
        logger.error(f"❌ TEST FAILED: {str(e)}")
        return False

def test_companies_proxy():
    """Test POST request to companies-proxy endpoint."""
    logger.info("Testing POST request to companies-proxy endpoint...")
    
    # Data to send
    data = {
        "name": "Companies Proxy POST Test",
        "description": "This tests the POST request to the companies-proxy endpoint",
        "brand_colors": ["#AABBCC", "#CCBBAA"]
    }
    
    headers = {
        "Content-Type": "application/json",
        "Authorization": f"Bearer {TEST_TOKEN}"
    }
    
    try:
        # Send the request
        response = requests.post(
            f"{API_BASE_URL}/companies-proxy/{COMPANY_ID}",
            headers=headers,
            json=data
        )
        
        # Print detailed info
        logger.info(f"Status Code: {response.status_code}")
        logger.info(f"Headers: {dict(response.headers)}")
        logger.info(f"Response Content: {response.text}")
        
        # Check if successful
        if response.status_code == 200:
            logger.info("✅ TEST PASSED: POST request to companies-proxy endpoint is successful!")
            return True
        else:
            logger.error(f"❌ TEST FAILED: POST request to companies-proxy failed with status {response.status_code}")
            return False
    except Exception as e:
        logger.error(f"❌ TEST FAILED: {str(e)}")
        return False

def main():
    """Run all tests."""
    logger.info("===== STARTING POST METHOD TESTS =====")
    
    # Wait for API server to be ready
    logger.info("Waiting for API server to be ready...")
    time.sleep(2)
    
    # Run tests
    test_results = {
        "POST company": test_post_company(),
        "PUT company": test_put_company(),
        "GET company": test_get_company(),
        "POST companies-proxy": test_companies_proxy(),
    }
    
    # Summary
    logger.info("\n===== TEST SUMMARY =====")
    all_passed = True
    for test_name, result in test_results.items():
        logger.info(f"{test_name}: {'PASSED' if result else 'FAILED'}")
        if not result:
            all_passed = False
    
    if all_passed:
        logger.info("\n🎉 ALL TESTS PASSED! POST method is working correctly!")
        return 0
    else:
        logger.error("\n❌ SOME TESTS FAILED. Please check the logs for details.")
        return 1

if __name__ == "__main__":
    sys.exit(main())
