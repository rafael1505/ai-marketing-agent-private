import requests
import os
import json

# Disable proxy for local connections
os.environ["HTTP_PROXY"] = ""
os.environ["HTTPS_PROXY"] = ""
os.environ["NO_PROXY"] = "*"

# Use the test token from deps.py
token = "eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9.eyJzdWIiOiJ0ZXN0QGV4YW1wbGUuY29tIiwibmFtZSI6IlRlc3QgVXNlciIsImlhdCI6MTY5NDYxMjMxMCwiZXhwIjo0ODQ4MzcyMzEwfQ.YourSignatureHere"

print("Testing authentication with hardcoded token from deps.py")
headers = {"Authorization": f"Bearer {token}"}
user_url = "http://127.0.0.1:8089/api/v1/users/me"

try:
    response = requests.get(user_url, headers=headers)
    print(f"Status code: {response.status_code}")
    if response.status_code == 200:
        user = response.json()
        print(f"User data: {json.dumps(user, indent=2)}")
    else:
        print(f"Error: {response.text}")
except Exception as e:
    print(f"Exception: {str(e)}")
