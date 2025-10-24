#!/usr/bin/env python3
import logging
import requests
import json
import time
import sys

# Configure logging
logging.basicConfig(
    level=logging.DEBUG,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
    handlers=[
        logging.StreamHandler(sys.stdout)
    ]
)

logger = logging.getLogger("login_test")

def test_login():
    """
    Test the login endpoint with detailed debugging
    """
    url = "http://127.0.0.1:8088/api/v1/auth/login"
    
    # Form data for login
    data = {
        "username": "test@example.com",
        "password": "password"
    }
    
    logger.info(f"Sending login request to {url}")
    logger.info(f"With credentials: {data}")
    
    try:
        # Wait a bit to make sure server logs show up first
        time.sleep(2)
        
        # Enable request debugging
        requests_log = logging.getLogger("urllib3")
        requests_log.setLevel(logging.DEBUG)
        
        # Send POST request to the login endpoint
        response = requests.post(
            url,
            data=data,
            headers={"Content-Type": "application/x-www-form-urlencoded"}
        )
        
        # Print the status code and response
        logger.info(f"Status code: {response.status_code}")
        logger.info(f"Response headers: {response.headers}")
        
        # Try to parse response as JSON if possible
        try:
            response_json = response.json()
            logger.info(f"Response body (JSON): {json.dumps(response_json, indent=2)}")
        except:
            logger.info(f"Response body (text): {response.text}")
            
        # Sleep to allow server logs to be processed
        time.sleep(2)
        
    except Exception as e:
        logger.error(f"Error during request: {e}")

if __name__ == "__main__":
    test_login()
