#!/usr/bin/env python3
"""
Comprehensive Company Persistence Test
This script tests both the API and direct DB access to ensure company data persistence
"""

import asyncio
import requests
import json
import sys
import time
import uuid
import os

# Add project directory to Python path
sys.path.append(os.path.abspath('.'))

# API configuration
BASE_URL = "http://127.0.0.1:8088"
AUTH_TOKEN = "DEVELOPMENT_MOCK_TOKEN_FOR_TESTING"
AUTH_HEADERS = {"Authorization": f"Bearer {AUTH_TOKEN}"}

# Colors for terminal output
GREEN = '\033[92m'
RED = '\033[91m'
YELLOW = '\033[93m'
BLUE = '\033[94m'
RESET = '\033[0m'

def print_color(color, message):
    """Print colored output"""
    print(f"{color}{message}{RESET}")

def print_section(title):
    """Print a formatted section header"""
    print("\n" + "=" * 50)
    print_color(BLUE, f"  {title}")
    print("=" * 50)

def print_success(message):
    """Print a success message"""
    print_color(GREEN, f"✓ {message}")

def print_error(message):
    """Print an error message"""
    print_color(RED, f"✗ {message}")

def print_warning(message):
    """Print a warning message"""
    print_color(YELLOW, f"! {message}")

def check_api_health():
    """Check if API is responsive"""
    try:
        response = requests.get(f"{BASE_URL}/api/v1/diagnostic/health")
        return response.status_code == 200
    except Exception:
        return False

def get_company_api():
    """Get active company through API"""
    try:
        response = requests.get(f"{BASE_URL}/api/v1/companies/active", headers=AUTH_HEADERS)
        if response.status_code == 200:
            return response.json()
        else:
            print_error(f"API returned status {response.status_code}")
            print(response.text)
            return None
    except Exception as e:
        print_error(f"API request error: {e}")
        return None

def update_company_api(company_id, data):
    """Update company through API"""
    form_data = {}
    
    # Add basic fields
    for key, value in data.items():
        if key != "brand_colors":
            form_data[key] = value
    
    # Add brand colors as simple repeated fields (matches the frontend fix)
    if "brand_colors" in data and data["brand_colors"]:
        for color in data["brand_colors"]:
            # This matches how formdata_array_fix.py expects arrays
            form_data["brand_colors"] = color
    
    try:
        response = requests.put(
            f"{BASE_URL}/api/v1/companies/{company_id}",
            data=form_data,
            headers=AUTH_HEADERS
        )
        if response.status_code == 200:
            return response.json()
        else:
            print_error(f"API returned status {response.status_code}")
            print(response.text)
            return None
    except Exception as e:
        print_error(f"API request error: {e}")
        return None

async def get_company_db():
    """Get active company directly from database"""
    try:
        from app.db.simple_mock_db import SimpleMockDatabase
        from app.db.company import CompanyDB
        
        # Initialize DB and get company
        mock_db = SimpleMockDatabase()
        company_db = CompanyDB(mock_db.companies)
        company = await company_db.get_active_company()
        return company
    except Exception as e:
        print_error(f"DB error: {e}")
        return None

async def update_company_db(company_id, data):
    """Update company directly in database"""
    try:
        from app.db.simple_mock_db import SimpleMockDatabase
        from app.db.company import CompanyDB
        from app.models.company import CompanyUpdate
        
        # Initialize DB
        mock_db = SimpleMockDatabase()
        company_db = CompanyDB(mock_db.companies)
        
        # Create update object
        update_data = CompanyUpdate(**data)
        
        # Perform update
        result = await company_db.update_company(company_id, update_data)
        return result
    except Exception as e:
        print_error(f"DB update error: {e}")
        import traceback
        traceback.print_exc()
        return None

async def run_tests():
    """Run all persistence tests"""
    print_section("COMPANY PERSISTENCE TESTS")
    
    # Check API health
    if not check_api_health():
        print_error("API is not responding. Please check the API server.")
        return
    print_success("API is running and healthy")
    
    # Test 1: API-based update and verification
    print_section("TEST 1: API UPDATE")
    
    # Get initial company
    company = get_company_api()
    if not company:
        print_error("Could not retrieve company via API")
        return
    
    company_id = company.get("id")
    print(f"Current company ID: {company_id}")
    print(f"Current company name: {company.get('name')}")
    print(f"Current brand colors: {company.get('brand_colors')}")
    
    # Generate unique test data
    test_id = uuid.uuid4().hex[:6]
    test_name = f"Company {test_id}"
    test_colors = [f"#{test_id}1", f"#{test_id}2"]
    
    # Prepare update data
    update_data = {
        "name": test_name,
        "description": "API persistence test",
        "brand_colors": test_colors
    }
    
    print(f"\nUpdating company with:")
    print(f"- Name: {test_name}")
    print(f"- Colors: {test_colors}")
    
    # Update company
    updated = update_company_api(company_id, update_data)
    if not updated:
        print_error("Company update failed")
        return
    
    # Verify immediately after update
    if updated.get("name") == test_name:
        print_success("Name updated successfully in response")
    else:
        print_error(f"Name mismatch in update response. Got: {updated.get('name')}")
    
    update_colors = updated.get("brand_colors", [])
    if sorted(update_colors) == sorted(test_colors):
        print_success("Colors updated successfully in response")
    else:
        print_error(f"Colors mismatch in update response. Got: {update_colors}")
    
    # Wait briefly for changes to settle
    print("\nWaiting for changes to persist...")
    time.sleep(1)
    
    # Verify data persistence
    print("\nVerifying persistence by retrieving company again...")
    retrieved = get_company_api()
    if not retrieved:
        print_error("Could not retrieve updated company")
        return
    
    # Check name persistence
    if retrieved.get("name") == test_name:
        print_success("Name persisted successfully")
    else:
        print_error(f"Name did not persist. Expected: {test_name}, Got: {retrieved.get('name')}")
    
    # Check color persistence
    retrieved_colors = retrieved.get("brand_colors", [])
    if not retrieved_colors:
        print_error("No brand_colors found in retrieved company")
    elif sorted(retrieved_colors) == sorted(test_colors):
        print_success("Brand colors persisted successfully")
    else:
        print_error(f"Brand colors did not persist.\nExpected: {test_colors}\nGot: {retrieved_colors}")
    
    # Test 2: Database-level verification
    print_section("TEST 2: DB VERIFICATION")
    
    # Get company from database
    db_company = await get_company_db()
    if not db_company:
        print_error("Could not retrieve company from database")
        return
    
    # Check name in database
    if db_company.get("name") == test_name:
        print_success("Name matched in database")
    else:
        print_error(f"Name mismatch in database. Expected: {test_name}, Got: {db_company.get('name')}")
    
    # Check colors in database
    db_colors = db_company.get("brand_colors", [])
    if not db_colors:
        print_error("No brand_colors found in database")
    elif sorted(db_colors) == sorted(test_colors):
        print_success("Brand colors matched in database")
    else:
        print_error(f"Brand colors mismatch in database.\nExpected: {test_colors}\nGot: {db_colors}")
    
    # Test 3: Direct database update
    print_section("TEST 3: DIRECT DB UPDATE")
    
    # Generate new unique test data
    db_test_id = uuid.uuid4().hex[:6]
    db_test_name = f"DB-Company {db_test_id}"
    db_test_colors = [f"#{db_test_id}1", f"#{db_test_id}2", f"#{db_test_id}3"]
    
    # Prepare update data
    db_update_data = {
        "name": db_test_name,
        "description": "Direct DB persistence test",
        "brand_colors": db_test_colors
    }
    
    print(f"\nUpdating company directly in DB with:")
    print(f"- Name: {db_test_name}")
    print(f"- Colors: {db_test_colors}")
    
    # Update company in database
    db_updated = await update_company_db(company_id, db_update_data)
    if not db_updated:
        print_error("Direct DB update failed")
        return
    
    # Verify DB update was successful
    if db_updated.get("name") == db_test_name:
        print_success("Name updated successfully in DB response")
    else:
        print_error(f"Name mismatch in DB response. Got: {db_updated.get('name')}")
    
    db_update_colors = db_updated.get("brand_colors", [])
    if sorted(db_update_colors) == sorted(db_test_colors):
        print_success("Colors updated successfully in DB response")
    else:
        print_error(f"Colors mismatch in DB response. Got: {db_update_colors}")
    
    # Wait briefly for changes to settle
    print("\nWaiting for changes to propagate...")
    time.sleep(1)
    
    # Verify through API that changes from DB are visible
    print("\nVerifying changes via API...")
    api_verification = get_company_api()
    if not api_verification:
        print_error("Could not retrieve updated company via API")
        return
    
    # Check name propagation
    if api_verification.get("name") == db_test_name:
        print_success("DB changes to name are visible via API")
    else:
        print_error(f"DB name changes not visible via API. Expected: {db_test_name}, Got: {api_verification.get('name')}")
    
    # Check color propagation
    api_colors = api_verification.get("brand_colors", [])
    if not api_colors:
        print_error("No brand_colors found in API response after DB update")
    elif sorted(api_colors) == sorted(db_test_colors):
        print_success("DB changes to brand colors are visible via API")
    else:
        print_error(f"DB color changes not visible via API.\nExpected: {db_test_colors}\nGot: {api_colors}")
    
    print_section("TEST RESULTS")
    print_success("All tests completed!")
    print("Review the results above to determine if the persistence issue has been resolved.")

if __name__ == "__main__":
    print_color(BLUE, "\n=== COMPANY DATA PERSISTENCE TEST ===\n")
    asyncio.run(run_tests())
