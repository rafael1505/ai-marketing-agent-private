#!/usr/bin/env python3

import requests
import json
import asyncio
import sys
from datetime import datetime

# Constants
API_BASE_URL = "http://127.0.0.1:8088"
COMPANY_ID = "test_company" 
API_DEBUG_ENDPOINT = f"{API_BASE_URL}/api-debug/{COMPANY_ID}"
API_COMPANIES_ENDPOINT = f"{API_BASE_URL}/api/v1/companies/{COMPANY_ID}"
ACTIVE_COMPANY_ENDPOINT = f"{API_BASE_URL}/api/v1/companies/active"

# Test auth token - hardcoded for testing purposes
# In a real application, this would be obtained through proper authentication
TEST_AUTH_TOKEN = "eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9.eyJzdWIiOiIxIiwibmFtZSI6IlRlc3QgVXNlciIsImlzX2FkbWluIjp0cnVlLCJleHAiOjE3MjAwMDAwMDB9.DEVELOPMENT_MOCK_TOKEN"

def print_header(message):
    print(f"\n{'=' * 80}")
    print(f"  {message}")
    print(f"{'=' * 80}")

def print_section(message):
    print(f"\n{'-' * 40}")
    print(f"  {message}")
    print(f"{'-' * 40}")

def get_company(endpoint):
    """Get company info from specified endpoint"""
    try:
        response = requests.get(endpoint)
        if response.status_code == 200:
            return response.json()
        else:
            print(f"Error: Status code {response.status_code}")
            print(f"Response: {response.text}")
            return None
    except Exception as e:
        print(f"Exception: {str(e)}")
        return None

def update_company(auth_token=None):
    """Update company with new data"""
    headers = {}
    if auth_token:
        headers["Authorization"] = f"Bearer {auth_token}"
    
    # Update data with timestamp to verify changes
    current_time = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
    data = {
        "name": f"Updated Company - {current_time}",
        "description": f"This is an updated description - {current_time}",
        "brand_colors": ["#FF5733", "#33FF57", "#3357FF"]
    }
    
    # Try API debug endpoint first (no auth)
    try:
        print_section("Trying API debug endpoint (no auth)")
        response = requests.put(API_DEBUG_ENDPOINT, json=data)
        print(f"Status: {response.status_code}")
        print(f"Response: {response.text[:100]}")  # Truncate long responses
        
        if response.status_code == 200:
            return "debug_endpoint", response
    except Exception as e:
        print(f"Debug endpoint error: {str(e)}")
    
    # Try regular endpoint with auth
    try:
        print_section("Trying regular API endpoint with auth")
        response = requests.put(API_COMPANIES_ENDPOINT, headers=headers, json=data)
        print(f"Status: {response.status_code}")
        print(f"Response: {response.text[:100]}")  # Truncate long responses
        
        if response.status_code == 200:
            return "auth_endpoint", response
    except Exception as e:
        print(f"Auth endpoint error: {str(e)}")
    
    return None, None

def verify_update(original, updated):
    """Compare original and updated company data to verify changes were made"""
    if not original or not updated:
        return False
    
    changes = []
    
    # Check name change
    if original.get("name") != updated.get("name"):
        changes.append(f"Name changed: {original.get('name')} -> {updated.get('name')}")
    
    # Check description change
    if original.get("description") != updated.get("description"):
        changes.append(f"Description changed: {original.get('description')} -> {updated.get('description')}")
    
    # Check brand_colors change
    orig_colors = original.get("brand_colors", [])
    upd_colors = updated.get("brand_colors", [])
    if orig_colors != upd_colors:
        changes.append(f"Colors changed: {orig_colors} -> {upd_colors}")
    
    if changes:
        print("\nVerified changes:")
        for change in changes:
            print(f"  ✓ {change}")
        return True
    else:
        print("\n❌ No changes detected between original and updated company data!")
        return False

def main():
    print_header("COMPANY PERSISTENCE TEST")
    
    # Step 1: Get current company
    print_section("STEP 1: Get current company state")
    original_company = get_company(ACTIVE_COMPANY_ENDPOINT)
    if original_company:
        print(f"Current company: {original_company.get('name', 'Unknown')}")
        print(f"Description: {original_company.get('description', 'None')}")
        print(f"Brand colors: {original_company.get('brand_colors', [])}")
    else:
        print("Could not retrieve current company!")
        return
    
    # Step 2: Update company
    print_section("STEP 2: Update company")
    success_source, update_response = update_company(TEST_AUTH_TOKEN)
    
    if not success_source:
        print("Failed to update company through any endpoint!")
        return
    
    print(f"✓ Update successful via {success_source}")
    
    # Step 3: Get company again to verify persistence
    print_section("STEP 3: Verify persistence")
    updated_company = get_company(ACTIVE_COMPANY_ENDPOINT)
    if updated_company:
        print(f"Updated company: {updated_company.get('name', 'Unknown')}")
        print(f"Updated description: {updated_company.get('description', 'None')}")
        print(f"Updated brand colors: {updated_company.get('brand_colors', [])}")
        
        # Verify changes
        changes_verified = verify_update(original_company, updated_company)
        
        if changes_verified:
            print("\n✅ PERSISTENCE TEST PASSED: Changes were successfully saved and retrieved!")
        else:
            print("\n❌ PERSISTENCE TEST FAILED: Company data was not properly updated!")
    else:
        print("Failed to retrieve updated company!")

if __name__ == "__main__":
    main()
