import requests
import json
import logging

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
    
    logger.info(f"Testing login at {endpoint} with {data}")
    
    try:
        response = requests.post(
            endpoint,
            data=data,  # Send as form data
            headers={"Content-Type": "application/x-www-form-urlencoded"}
        )
        
        logger.info(f"Status code: {response.status_code}")
        
        if response.status_code == 200:
            response_data = response.json()
            logger.info("Login successful!")
            logger.info(f"Response: {json.dumps(response_data, indent=2)}")
            return True, response_data
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

if __name__ == "__main__":
    success, token_data = test_login()
    if success:
        print("\n✅ Login test passed!\n")
    else:
        print("\n❌ Login test failed!\n")
