#!/usr/bin/env python3

"""
Test script for FormData submissions to the company update endpoint.
This script simulates different FormData submission methods to test the API's handling.
"""

import sys
import aiohttp
import asyncio
import json
import logging
from urllib.parse import urljoin
import os
from datetime import datetime

# Set up logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(levelname)s - %(message)s',
    handlers=[
        logging.StreamHandler(sys.stdout),
        logging.FileHandler(f'formdata_test_{datetime.now().strftime("%Y%m%d_%H%M%S")}.log')
    ]
)
logger = logging.getLogger(__name__)

# Configuration
BASE_URL = "http://localhost:8088"  # Change to your API server URL
COMPANY_ID = "test_company"  # Change to your test company ID
AUTH_TOKEN_PATH = "auth_token.json"  # Path to auth token file

async def load_auth_token():
    """Load authentication token from file"""
    try:
        if os.path.exists(AUTH_TOKEN_PATH):
            with open(AUTH_TOKEN_PATH, 'r') as f:
                data = json.load(f)
                return data.get('access_token')
        else:
            logger.error(f"Auth token file not found: {AUTH_TOKEN_PATH}")
            return None
    except Exception as e:
        logger.error(f"Error loading auth token: {str(e)}")
        return None

async def test_json_submission(session, token):
    """Test JSON-based company update submission"""
    logger.info("Testing JSON submission...")
    
    url = urljoin(BASE_URL, f"/api/v1/companies/{COMPANY_ID}")
    headers = {
        "Authorization": f"Bearer {token}",
        "Content-Type": "application/json"
    }
    data = {
        "name": "JSON Test Company",
        "description": "This is a test using JSON submission",
        "brand_colors": ["#3B82F6", "#93C5FD"]
    }
    
    try:
        async with session.put(url, headers=headers, json=data) as response:
            status = response.status
            try:
                response_data = await response.json()
            except:
                response_data = await response.text()
                
            logger.info(f"JSON submission status: {status}")
            logger.info(f"JSON submission response: {response_data}")
            return status == 200
    except Exception as e:
        logger.error(f"Error in JSON submission: {str(e)}")
        return False

async def test_formdata_submission(session, token, content_type=None):
    """Test FormData-based company update submission"""
    content_type_str = content_type or "Auto (browser-determined)"
    logger.info(f"Testing FormData submission with Content-Type: {content_type_str}...")
    
    url = urljoin(BASE_URL, f"/api/v1/companies/{COMPANY_ID}")
    headers = {
        "Authorization": f"Bearer {token}",
    }
    
    if content_type:
        headers["Content-Type"] = content_type
    
    # Prepare form data
    form_data = aiohttp.FormData()
    form_data.add_field("name", "FormData Test Company")
    form_data.add_field("description", f"This is a test using FormData with {content_type_str}")
    
    # Try different brand_colors formats
    if content_type_str == "Auto (browser-determined)":
        # Test JSON stringified array
        form_data.add_field("brand_colors", json.dumps(["#3B82F6", "#93C5FD"]))
    elif "multipart" in content_type_str:
        # Test indexed notation
        form_data.add_field("brand_colors[0]", "#3B82F6")
        form_data.add_field("brand_colors[1]", "#93C5FD")
    else:
        # Test comma-separated
        form_data.add_field("brand_colors", "#3B82F6,#93C5FD")
    
    try:
        async with session.put(url, headers=headers, data=form_data) as response:
            status = response.status
            try:
                response_data = await response.json()
            except:
                response_data = await response.text()
                
            logger.info(f"FormData submission status: {status}")
            logger.info(f"FormData submission response: {response_data}")
            return status == 200
    except Exception as e:
        logger.error(f"Error in FormData submission: {str(e)}")
        return False

async def verify_company_data(session, token):
    """Verify company data was updated correctly"""
    logger.info("Verifying company data...")
    
    url = urljoin(BASE_URL, f"/api/v1/companies/{COMPANY_ID}")
    headers = {
        "Authorization": f"Bearer {token}"
    }
    
    try:
        async with session.get(url, headers=headers) as response:
            status = response.status
            try:
                response_data = await response.json()
            except:
                response_data = await response.text()
                
            logger.info(f"Verification status: {status}")
            logger.info(f"Company data: {response_data}")
            return status == 200, response_data
    except Exception as e:
        logger.error(f"Error verifying company data: {str(e)}")
        return False, None

async def main():
    """Main test function"""
    logger.info("Starting FormData submission tests...")
    
    token = await load_auth_token()
    if not token:
        logger.error("No authentication token found. Please login first.")
        return
    
    async with aiohttp.ClientSession() as session:
        # Test JSON submission
        json_success = await test_json_submission(session, token)
        logger.info(f"JSON submission {'successful' if json_success else 'failed'}")
        
        # Test FormData submission with different content types
        form_auto_success = await test_formdata_submission(session, token)
        logger.info(f"FormData (auto) submission {'successful' if form_auto_success else 'failed'}")
        
        form_multipart_success = await test_formdata_submission(
            session, token, "multipart/form-data"
        )
        logger.info(
            f"FormData (multipart) submission {'successful' if form_multipart_success else 'failed'}"
        )
        
        # Verify final company data
        verification_success, company_data = await verify_company_data(session, token)
        
        # Summary
        logger.info("\n===== TEST SUMMARY =====")
        logger.info(f"JSON submission: {'✅' if json_success else '❌'}")
        logger.info(f"FormData (auto) submission: {'✅' if form_auto_success else '❌'}")
        logger.info(f"FormData (multipart) submission: {'✅' if form_multipart_success else '❌'}")
        logger.info(f"Verification: {'✅' if verification_success else '❌'}")
        
        if verification_success and company_data:
            logger.info(f"Final brand_colors: {company_data.get('brand_colors', [])}")

if __name__ == "__main__":
    asyncio.run(main())
