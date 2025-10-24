#!/usr/bin/env python3
"""
Final test for company persistence, with output to terminal
"""
import requests
import time
import uuid
import sys

# ANSI colors for terminal output
GREEN = '\033[92m'
RED = '\033[91m'
YELLOW = '\033[93m'
BLUE = '\033[94m'
RESET = '\033[0m'

def print_color(color, message):
    """Print colored text"""
    print(f"{color}{message}{RESET}")

# Configuration
BASE_URL = "http://127.0.0.1:8088"
AUTH_TOKEN = "DEVELOPMENT_MOCK_TOKEN_FOR_TESTING"
AUTH_HEADERS = {"Authorization": f"Bearer {AUTH_TOKEN}"}

# First check if API is responding
try:
    response = requests.get(f"{BASE_URL}/api/v1/diagnostic/health")
    if response.status_code != 200:
        print_color(RED, f"API not responding properly. Status code: {response.status_code}")
        sys.exit(1)
    print_color(GREEN, "API is running and healthy")
except Exception as e:
    print_color(RED, f"Error connecting to API: {e}")
    sys.exit(1)

# Get current company
print_color(BLUE, "\n1. Getting current company data...")
try:
    response = requests.get(f"{BASE_URL}/api/v1/companies/active", headers=AUTH_HEADERS)
    if response.status_code != 200:
        print_color(RED, f"Error getting company: {response.status_code} - {response.text}")
        sys.exit(1)
    
    company = response.json()
    print(f"Current company: {company['name']}")
    print(f"Current colors: {company.get('brand_colors')}")
    company_id = company.get('id')
except Exception as e:
    print_color(RED, f"Request error: {e}")
    sys.exit(1)

# Generate unique test colors
test_id = uuid.uuid4().hex[:6]
test_colors = [f"#TEST{test_id}1", f"#TEST{test_id}2"]

# Update the company
print_color(BLUE, f"\n2. Updating company with test colors: {test_colors}")
update_data = {
    "name": f"Test Company {test_id}",
    "description": "Color persistence test"
}

# Add colors with array indexing
for i, color in enumerate(test_colors):
    update_data[f"brand_colors[{i}]"] = color

try:
    response = requests.put(
        f"{BASE_URL}/api/v1/companies/{company_id}",
        data=update_data,
        headers=AUTH_HEADERS
    )
    
    if response.status_code != 200:
        print_color(RED, f"Update failed: {response.status_code} - {response.text}")
        sys.exit(1)
    
    updated = response.json()
    print("Update response received:")
    print(f"- Name: {updated.get('name')}")
    print(f"- Colors: {updated.get('brand_colors')}")
except Exception as e:
    print_color(RED, f"Update error: {e}")
    sys.exit(1)

# Wait for changes to take effect
print_color(YELLOW, "\nWaiting for changes to persist...")
time.sleep(1)

# Get the updated company
print_color(BLUE, "\n3. Retrieving company to check persistence...")
try:
    response = requests.get(f"{BASE_URL}/api/v1/companies/active", headers=AUTH_HEADERS)
    if response.status_code != 200:
        print_color(RED, f"Error getting updated company: {response.status_code} - {response.text}")
        sys.exit(1)
    
    final = response.json()
    print(f"Retrieved company:")
    print(f"- Name: {final.get('name')}")
    print(f"- Colors: {final.get('brand_colors')}")
except Exception as e:
    print_color(RED, f"Retrieval error: {e}")
    sys.exit(1)

# Verify persistence
print_color(BLUE, "\n4. Verifying data persistence...")

name_persisted = final.get('name') == update_data['name']
colors_persisted = sorted(final.get('brand_colors', [])) == sorted(test_colors)

if name_persisted:
    print_color(GREEN, "✓ Name change persisted successfully")
else:
    print_color(RED, f"✗ Name did not persist. Expected: {update_data['name']}, Got: {final.get('name')}")

if colors_persisted:
    print_color(GREEN, "✓ Brand colors persisted successfully")
else:
    print_color(RED, f"✗ Brand colors did not persist properly")
    print(f"  Expected: {test_colors}")
    print(f"  Got: {final.get('brand_colors', [])}")

if name_persisted and colors_persisted:
    print_color(GREEN, "\n✓ SUCCESS! All data persisted correctly. The fix is working!")
else:
    print_color(RED, "\n✗ FAILURE! Data not persisting correctly. Issue remains.")
