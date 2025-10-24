#!/usr/bin/env python3
"""
Test script for FormData array parsing in the company update API.
This script simulates different FormData formats to ensure brand_colors are processed correctly.
"""

import requests
import json
import logging
import sys

# Configure logging
logging.basicConfig(level=logging.INFO, 
                   format='%(asctime)s - %(name)s - %(levelname)s - %(message)s')
logger = logging.getLogger("FormDataArrayTest")

def test_company_formdata_formats():
    """Test different FormData formats for brand_colors to ensure they all work"""
    base_url = "http://127.0.0.1:8088"
    company_id = "test_company"
    
    # Step 1: Get current company state
    logger.info("Getting current company info...")
    response = requests.get(f"{base_url}/api/v1/companies/active", 
                            proxies={"http": None, "https": None})
    
    if response.status_code != 200:
        logger.error(f"Failed to get company: {response.status_code}")
        logger.error(response.text)
        return False
    
    company = response.json()
    logger.info(f"Current company: {company['name']}")
    logger.info(f"Current colors: {company.get('brand_colors', [])}")
    
    # Step 2: Get a mock auth token for testing
    mock_token = "DEVELOPMENT_MOCK_TOKEN_FOR_TESTING"
    
    # Test each FormData format
    test_cases = [
        {
            "name": "Standard FormData (multipart/form-data)",
            "content_type": "multipart/form-data",
            "data": {
                "name": "FormData Test Company (Standard)",
                "description": "Testing standard FormData",
                "brand_colors[0]": "#FF0000",
                "brand_colors[1]": "#00FF00",
                "brand_colors[2]": "#0000FF"
            },
            "expected_colors": ["#FF0000", "#00FF00", "#0000FF"],
        },
        {
            "name": "JSON Array Format",
            "content_type": "multipart/form-data",
            "data": {
                "name": "FormData Test Company (JSON Array)",
                "description": "Testing JSON array in FormData",
                "brand_colors": json.dumps(["#112233", "#445566", "#778899"])
            },
            "expected_colors": ["#112233", "#445566", "#778899"],
        },
        {
            "name": "Comma-Separated Values",
            "content_type": "multipart/form-data",
            "data": {
                "name": "FormData Test Company (CSV)",
                "description": "Testing comma-separated values",
                "brand_colors": "#AABBCC, #DDEEFF, #123456"
            },
            "expected_colors": ["#AABBCC", "#DDEEFF", "#123456"],
        }
    ]
    
    results = []
    
    for test_case in test_cases:
        logger.info(f"\n--- Running test: {test_case['name']} ---")
        
        headers = {
            "Authorization": f"Bearer {mock_token}"
        }
        
        # For multipart/form-data, we don't set content-type manually
        # as requests will set it with the correct boundary
        
        response = requests.put(
            f"{base_url}/api/v1/companies/{company_id}",
            data=test_case["data"],
            headers=headers,
            proxies={"http": None, "https": None}
        )
        
        logger.info(f"Status code: {response.status_code}")
        
        if response.status_code >= 400:
            logger.error(f"Error: {response.text}")
            results.append({
                "test": test_case["name"],
                "success": False,
                "error": response.text
            })
            continue
            
        # Verify the response contains the updated company
        try:
            response_data = response.json()
            
            if "company" in response_data:
                updated_company = response_data["company"]
                actual_colors = updated_company.get("brand_colors", [])
            else:
                actual_colors = response_data.get("brand_colors", [])
                
            logger.info(f"Actual colors in response: {actual_colors}")
            
            # Check again with a fresh GET request to verify persistence
            verify_response = requests.get(f"{base_url}/api/v1/companies/active", 
                                          proxies={"http": None, "https": None})
            
            if verify_response.status_code == 200:
                verify_data = verify_response.json()
                persisted_colors = verify_data.get("brand_colors", [])
                logger.info(f"Persisted colors: {persisted_colors}")
                
                # Compare with expected colors (ignoring order)
                expected_sorted = sorted(test_case["expected_colors"])
                actual_sorted = sorted(persisted_colors)
                match = expected_sorted == actual_sorted
                
                if match:
                    logger.info("✅ PASS: Colors persisted correctly")
                else:
                    logger.error(f"❌ FAIL: Colors did not persist correctly")
                    logger.error(f"Expected: {expected_sorted}")
                    logger.error(f"Actual: {actual_sorted}")
                
                results.append({
                    "test": test_case["name"],
                    "success": match,
                    "expected": test_case["expected_colors"],
                    "actual": persisted_colors
                })
            else:
                logger.error(f"Failed to verify persistence: {verify_response.status_code}")
                results.append({
                    "test": test_case["name"],
                    "success": False,
                    "error": f"Verification failed: {verify_response.status_code}"
                })
        except Exception as e:
            logger.error(f"Error processing response: {str(e)}")
            results.append({
                "test": test_case["name"],
                "success": False,
                "error": str(e)
            })
    
    # Print summary
    logger.info("\n--- Test Results Summary ---")
    passed = sum(1 for r in results if r["success"])
    failed = sum(1 for r in results if not r["success"])
    
    for result in results:
        status = "✅ PASS" if result["success"] else "❌ FAIL"
        logger.info(f"{status}: {result['test']}")
        if not result["success"] and "error" in result:
            logger.info(f"  Error: {result['error']}")
    
    logger.info(f"\nTotal: {len(results)}, Passed: {passed}, Failed: {failed}")
    
    return failed == 0

if __name__ == "__main__":
    logger.info("Starting FormData array parsing test")
    success = test_company_formdata_formats()
    
    if success:
        logger.info("\n✅ All tests passed! The FormData array parsing fix is working correctly.")
        sys.exit(0)
    else:
        logger.error("\n❌ Some tests failed. The FormData array parsing fix needs more work.")
        sys.exit(1)
