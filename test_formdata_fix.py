#!/usr/bin/env python3

"""
Test script to verify FormData array handling in the API
"""

import requests
import json
import logging
import os
from typing import Dict, Any, List

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger(__name__)

# API configuration
API_BASE_URL = "http://127.0.0.1:8088/api/v1"
COMPANY_ID = "test_company"

def get_test_token() -> str:
    """Get a development token for testing"""
    auth_data = {
        "username": "test@example.com",
        "password": "password"
    }
    
    try:
        auth_response = requests.post(
            f"{API_BASE_URL}/auth/token",
            data=auth_data,
            headers={"Content-Type": "application/x-www-form-urlencoded"}
        )
        
        if auth_response.status_code == 200:
            token_data = auth_response.json()
            return token_data.get("access_token")
        else:
            logger.error(f"Authentication failed: {auth_response.status_code}")
            logger.error(f"Response: {auth_response.text}")
            return "DEVELOPMENT_MOCK_TOKEN_FOR_TESTING"
    except Exception as e:
        logger.error(f"Error getting token: {str(e)}")
        return "DEVELOPMENT_MOCK_TOKEN_FOR_TESTING"

def get_active_company(token: str) -> Dict[str, Any]:
    """Get the active company details"""
    try:
        response = requests.get(
            f"{API_BASE_URL}/companies/active",
            headers={"Authorization": f"Bearer {token}"}
        )
        
        if response.status_code == 200:
            return response.json()
        else:
            logger.error(f"Get company failed: {response.status_code}")
            logger.error(f"Response: {response.text}")
            return {}
    except Exception as e:
        logger.error(f"Error getting company: {str(e)}")
        return {}

def test_debug_endpoint(token: str) -> bool:
    """Test the debug FormData endpoint"""
    logger.info("Testing FormData debug endpoint...")
    
    # Test with various FormData array formats
    files = {}
    
    # Method 1: Array with indexed notation
    data1 = {
        "name": "FormData Test (indexed notation)",
        "description": "Testing with indexed array notation",
        "brand_colors[0]": "#FF5733",
        "brand_colors[1]": "#33FF57",
        "brand_colors[2]": "#3357FF"
    }
    
    try:
        response = requests.post(
            f"{API_BASE_URL}/companies/debug-formdata",
            headers={"Authorization": f"Bearer {token}"},
            data=data1,
            files=files
        )
        
        logger.info(f"Debug endpoint response (indexed): {response.status_code}")
        if response.status_code == 200:
            result = response.json()
            logger.info(f"Parsed arrays: {result.get('parsed_arrays')}")
            logger.info(f"Raw keys: {result.get('raw_keys')}")
            
            # Verify the array was parsed correctly
            parsed_brand_colors = result.get('parsed_arrays', {}).get('brand_colors')
            if parsed_brand_colors and len(parsed_brand_colors) == 3:
                logger.info("✓ Indexed array notation parsed correctly")
            else:
                logger.error("✗ Indexed array notation not parsed correctly")
                return False
        else:
            logger.error(f"Debug endpoint failed: {response.text}")
            return False
    except Exception as e:
        logger.error(f"Error testing debug endpoint: {str(e)}")
        return False
    
    # Method 2: JSON stringified array
    data2 = {
        "name": "FormData Test (JSON string)",
        "description": "Testing with JSON stringified array",
        "brand_colors": json.dumps(["#FF5733", "#33FF57", "#3357FF"])
    }
    
    try:
        response = requests.post(
            f"{API_BASE_URL}/companies/debug-formdata",
            headers={"Authorization": f"Bearer {token}"},
            data=data2,
            files=files
        )
        
        logger.info(f"Debug endpoint response (JSON string): {response.status_code}")
        if response.status_code == 200:
            result = response.json()
            logger.info(f"Parsed arrays: {result.get('parsed_arrays')}")
            logger.info(f"Raw keys: {result.get('raw_keys')}")
            
            # Verify the array was parsed correctly
            parsed_brand_colors = result.get('parsed_arrays', {}).get('brand_colors')
            if parsed_brand_colors and len(parsed_brand_colors) == 3:
                logger.info("✓ JSON stringified array parsed correctly")
            else:
                logger.error("✗ JSON stringified array not parsed correctly")
                return False
        else:
            logger.error(f"Debug endpoint failed: {response.text}")
            return False
    except Exception as e:
        logger.error(f"Error testing debug endpoint: {str(e)}")
        return False
    
    return True

def test_company_update(token: str) -> bool:
    """Test updating company with brand colors"""
    logger.info("Testing company update with brand colors...")
    
    # Get current company first
    company = get_active_company(token)
    if not company:
        logger.error("Couldn't get active company")
        return False
    
    company_id = company.get("id", COMPANY_ID)
    logger.info(f"Current company: {company.get('name')}")
    logger.info(f"Current colors: {company.get('brand_colors', [])}")
    
    # Update with new brand colors using indexed notation
    new_colors = ["#AA1122", "#22AA11", "#1122AA"]
    
    # Method 1: Using indexed notation
    data = {
        "name": "Updated Colors (indexed)",
        "description": company.get("description", ""),
        "email": company.get("email", "test@example.com"),
        "phone": company.get("phone", ""),
        "address": company.get("address", ""),
        "logo_url": company.get("logo_url", "")
    }
    
    # Add colors with indexed notation
    for i, color in enumerate(new_colors):
        data[f"brand_colors[{i}]"] = color
    
    try:
        response = requests.put(
            f"{API_BASE_URL}/companies/{company_id}",
            headers={"Authorization": f"Bearer {token}"},
            data=data
        )
        
        logger.info(f"Update response (indexed): {response.status_code}")
        if response.status_code == 200:
            result = response.json()
            logger.info(f"Updated company: {result.get('name')}")
            logger.info(f"Updated colors: {result.get('brand_colors', [])}")
            
            # Verify colors were updated
            updated_colors = result.get('brand_colors', [])
            if set(updated_colors) == set(new_colors):
                logger.info("✓ Colors updated correctly (indexed notation)")
            else:
                logger.error(f"✗ Colors not updated correctly. Expected {new_colors}, got {updated_colors}")
                return False
                
            # Check persistence
            get_response = requests.get(
                f"{API_BASE_URL}/companies/active",
                headers={"Authorization": f"Bearer {token}"}
            )
            
            if get_response.status_code == 200:
                check_company = get_response.json()
                check_colors = check_company.get('brand_colors', [])
                
                if set(check_colors) == set(new_colors):
                    logger.info("✓ Colors persist after retrieval")
                else:
                    logger.error(f"✗ Colors don't persist. Expected {new_colors}, got {check_colors}")
                    return False
            else:
                logger.error(f"Failed to verify colors: {get_response.status_code}")
                return False
        else:
            logger.error(f"Update failed: {response.text}")
            return False
    except Exception as e:
        logger.error(f"Error updating company: {str(e)}")
        return False
    
    # Method 2: Using JSON stringified array
    new_colors = ["#BB3344", "#44BB33", "#3344BB"]
    
    data = {
        "name": "Updated Colors (JSON)",
        "description": company.get("description", ""),
        "email": company.get("email", "test@example.com"),
        "phone": company.get("phone", ""),
        "address": company.get("address", ""),
        "logo_url": company.get("logo_url", ""),
        "brand_colors": json.dumps(new_colors)
    }
    
    try:
        response = requests.put(
            f"{API_BASE_URL}/companies/{company_id}",
            headers={"Authorization": f"Bearer {token}"},
            data=data
        )
        
        logger.info(f"Update response (JSON): {response.status_code}")
        if response.status_code == 200:
            result = response.json()
            logger.info(f"Updated company: {result.get('name')}")
            logger.info(f"Updated colors: {result.get('brand_colors', [])}")
            
            # Verify colors were updated
            updated_colors = result.get('brand_colors', [])
            if set(updated_colors) == set(new_colors):
                logger.info("✓ Colors updated correctly (JSON notation)")
            else:
                logger.error(f"✗ Colors not updated correctly. Expected {new_colors}, got {updated_colors}")
                return False
                
            # Check persistence
            get_response = requests.get(
                f"{API_BASE_URL}/companies/active",
                headers={"Authorization": f"Bearer {token}"}
            )
            
            if get_response.status_code == 200:
                check_company = get_response.json()
                check_colors = check_company.get('brand_colors', [])
                
                if set(check_colors) == set(new_colors):
                    logger.info("✓ Colors persist after retrieval")
                else:
                    logger.error(f"✗ Colors don't persist. Expected {new_colors}, got {check_colors}")
                    return False
            else:
                logger.error(f"Failed to verify colors: {get_response.status_code}")
                return False
        else:
            logger.error(f"Update failed: {response.text}")
            return False
    except Exception as e:
        logger.error(f"Error updating company: {str(e)}")
        return False
    
    return True

def main():
    """Main test function"""
    logger.info("Starting FormData array handling test...")
    
    # Get test token
    token = get_test_token()
    if not token:
        logger.error("Failed to get authentication token")
        return False
    
    # Run tests
    debug_ok = test_debug_endpoint(token)
    update_ok = test_company_update(token)
    
    # Report results
    all_passed = debug_ok and update_ok
    
    if all_passed:
        logger.info("\n✅ All FormData tests passed!")
    else:
        logger.error("\n❌ Some FormData tests failed!")
    
    return all_passed

if __name__ == "__main__":
    success = main()
    sys.exit(0 if success else 1)
