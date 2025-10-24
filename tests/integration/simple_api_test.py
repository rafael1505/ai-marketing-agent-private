import requests

# Base URL for the API server
API_URL = "http://127.0.0.1:8088"

def main():
    # Make a simple request to the API health endpoint
    print(f"Testing API connection to {API_URL}...")
    
    try:
        # Test diagnostic/ping endpoint
        response = requests.get(f"{API_URL}/api/v1/diagnostic/ping", timeout=5)
        if response.status_code == 200:
            print(f"✅ API Ping Test: OK ({response.status_code})")
            print(f"Response: {response.json()}")
        else:
            print(f"❌ API Ping Test: Failed ({response.status_code})")
            print(f"Response: {response.text}")
            return
        
        # Test diagnostic/health endpoint
        response = requests.get(f"{API_URL}/api/v1/diagnostic/health", timeout=5)
        if response.status_code == 200:
            print(f"✅ API Health Test: OK ({response.status_code})")
            print(f"Response: {response.json()}")
        else:
            print(f"❌ API Health Test: Failed ({response.status_code})")
            print(f"Response: {response.text}")
            return
            
        # Test authentication
        print("\nTesting authentication...")
        login_data = {"username": "test@example.com", "password": "password"}
        response = requests.post(
            f"{API_URL}/api/v1/auth/login", 
            data=login_data,
            timeout=5
        )
        
        if response.status_code == 200:
            print(f"✅ Authentication Test: OK ({response.status_code})")
            token_data = response.json()
            token = token_data.get("access_token")
            print(f"Retrieved token: {token[:20]}...")
            
            # Test protected endpoint
            headers = {"Authorization": f"Bearer {token}"}
            response = requests.get(
                f"{API_URL}/api/v1/users/me",
                headers=headers,
                timeout=5
            )
            
            if response.status_code == 200:
                print(f"✅ Protected Endpoint Test: OK ({response.status_code})")
                print(f"User data: {response.json()}")
            else:
                print(f"❌ Protected Endpoint Test: Failed ({response.status_code})")
                print(f"Response: {response.text}")
        else:
            print(f"❌ Authentication Test: Failed ({response.status_code})")
            print(f"Response: {response.text}")
            
    except requests.exceptions.RequestException as e:
        print(f"❌ Connection Error: {e}")
        
    print("\nAPI Connection Test Complete")

if __name__ == "__main__":
    main()
