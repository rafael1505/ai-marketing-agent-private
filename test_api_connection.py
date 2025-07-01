import requests
import sys
import logging

logging.basicConfig(level=logging.INFO, format="%(asctime)s - %(levelname)s - %(message)s")

API_URL = "http://localhost:8088"

def test_api_connection():
    """Test basic connection to the API server"""
    try:
        logging.info(f"Attempting to connect to API at {API_URL}")
        response = requests.get(f"{API_URL}/")
        logging.info(f"Response status: {response.status_code}")
        logging.info(f"Response content: {response.text[:100]}")
        return response.status_code == 200
    except requests.exceptions.ConnectionError as e:
        logging.error(f"Connection error: {e}")
        return False

def test_active_company():
    """Test the /api/v1/companies/active endpoint"""
    try:
        url = f"{API_URL}/api/v1/companies/active"
        logging.info(f"Testing endpoint: {url}")
        response = requests.get(url)
        logging.info(f"Response status: {response.status_code}")
        if response.status_code == 200:
            logging.info(f"Company data: {response.json()}")
            return True
        else:
            logging.error(f"Failed to get active company. Response: {response.text}")
            return False
    except Exception as e:
        logging.error(f"Error testing active company: {e}")
        return False
        
def main():
    if not test_api_connection():
        logging.error("API connection failed")
        return 1
        
    if not test_active_company():
        logging.error("Active company test failed")
        return 2
        
    logging.info("All tests passed!")
    return 0
    
if __name__ == "__main__":
    sys.exit(main())
