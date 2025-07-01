import requests

# Test the simplest endpoint
ping_url = "http://127.0.0.1:8089/api/v1/diagnostic/ping"
print(f"Testing ping endpoint at {ping_url}...")
try:
    ping_response = requests.get(ping_url)
    print(f"Status code: {ping_response.status_code}")
    print(f"Response: {ping_response.text}")
except Exception as e:
    print(f"Error: {str(e)}")

# Try another endpoint with no authentication
health_url = "http://127.0.0.1:8089/api/v1/diagnostic/health"
print(f"\nTesting health endpoint at {health_url}...")
try:
    health_response = requests.get(health_url)
    print(f"Status code: {health_response.status_code}")
    print(f"Response: {health_response.text}")
except Exception as e:
    print(f"Error: {str(e)}")
