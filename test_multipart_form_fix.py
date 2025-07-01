#!/usr/bin/env python3

"""
Test script for verifying the multipart/form-data without boundary fix.
"""

import requests
import json
import logging
import sys

# Set up logging
logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(levelname)s - %(message)s')
logger = logging.getLogger(__name__)

# Configuration
API_BASE_URL = "http://localhost:8088"
COMPANY_ID = "test_company"

# Test token - should match the one used in the auth-debug-suite.html
# This is a dummy token for testing purposes
TEST_TOKEN = "eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9.eyJzdWIiOiJ0ZXN0QGV4YW1wbGUuY29tIiwiZXhwIjoxNjUwMDAwMDAwfQ.1exampledevsignature"

def test_plain_multipart_form_data():
    """Test the multipart/form-data Content-Type without boundary parameter."""
    logger.info("Testing multipart/form-data without boundary...")
    
    # Data to send
    data = {
        "name": "Test multipart/form-data Fix",
        "description": "This tests the fix for multipart/form-data without boundary",
        "brand_colors": ["#FF5733", "#33FF57"]
    }
    
    headers = {
        "Content-Type": "multipart/form-data",  # Intentionally missing boundary
        "Authorization": f"Bearer {TEST_TOKEN}"
    }
    
    try:
        # Send the request
        response = requests.put(
            f"{API_BASE_URL}/api/v1/companies/{COMPANY_ID}",
            headers=headers,
            # Use json instead of data to force it to send as JSON body
            json=data
        )
        
        # Print detailed info
        logger.info(f"Status Code: {response.status_code}")
        logger.info(f"Headers: {dict(response.headers)}")
        logger.info(f"Response Content: {response.text}")
        
        # Check if successful
        try:
            json_response = response.json()
            logger.info(f"JSON Response: {json_response}")
            
            if response.status_code == 200:
                logger.info("✅ TEST PASSED: multipart/form-data without boundary is now working!")
                return True
            else:
                logger.error("❌ TEST FAILED: Request failed with error")
                return False
        except Exception as e:
            logger.error(f"❌ TEST FAILED: Could not parse response as JSON: {str(e)}")
            return False
    except Exception as e:
        logger.error(f"❌ TEST FAILED: Request error: {str(e)}")
        return False

def verify_company_data():
    """Verify the company data was properly updated."""
    logger.info("Verifying company data...")
    
    try:
        response = requests.get(f"{API_BASE_URL}/api/v1/companies/active")
        if response.status_code == 200:
            company = response.json()
            logger.info(f"Company data: {company}")
            
            # Verify that brand_colors is a list
            if isinstance(company.get('brand_colors'), list):
                logger.info("✅ VALIDATION PASSED: brand_colors is a list")
                return True
            else:
                logger.error(f"❌ VALIDATION FAILED: brand_colors is not a list: {company.get('brand_colors')}")
                return False
        else:
            logger.error(f"❌ VALIDATION FAILED: Could not get company data: {response.status_code} {response.text}")
            return False
    except Exception as e:
        logger.error(f"❌ VALIDATION FAILED: Error: {str(e)}")
        return False

def main():
    """Run all tests."""
    logger.info("Starting tests for multipart/form-data fix")
    
    # Test 1: multipart/form-data without boundary
    test_result = test_plain_multipart_form_data()
    
    # Test 2: Verify company data
    validation_result = verify_company_data()
    
    # Summary
    logger.info("=== TEST SUMMARY ===")
    logger.info(f"multipart/form-data test: {'PASSED' if test_result else 'FAILED'}")
    logger.info(f"Data validation test: {'PASSED' if validation_result else 'FAILED'}")
    
    # Exit with appropriate code
    if test_result and validation_result:
        logger.info("🎉 ALL TESTS PASSED!")
        sys.exit(0)
    else:
        logger.error("❌ SOME TESTS FAILED")
        sys.exit(1)

if __name__ == "__main__":
    main()
