#!/usr/bin/env python3
"""
Test Company Update and Persistence

This script verifies that:
1. The company can be updated through the API
2. The updates persist in the database
3. The updates can be retrieved from the API
"""

import requests
import json
import os
import sys
import datetime
import time

API_URL = "http://localhost:8088"
TEST_COMPANY_ID = "test_company"
AUTH_TOKEN_FILE = "auth_token.json"
DATABASE_PATH = "app/db/data/companies.json"

# New test data 
new_company_data = {
    "name": f"Persistence Test Company {datetime.datetime.now().strftime('%H:%M:%S')}",
    "description": "This company proves persistence works",
    "brand_colors": ["#2196F3", "#FFC107", "#4CAF50", "#E91E63", "#9C27B0"]
}

def get_auth_token():
    """Get authentication token from file"""
    try:
        if os.path.exists(AUTH_TOKEN_FILE):
            with open(AUTH_TOKEN_FILE, 'r') as f:
                token_data = json.load(f)
                return token_data.get("token")
        else:
            print(f"Auth token file not found at {AUTH_TOKEN_FILE}")
            return None
    except Exception as e:
        print(f"Error reading auth token: {e}")
        return None

def get_headers():
    """Get headers with authentication token"""
    token = get_auth_token()
    if token:
        return {"Authorization": f"Bearer {token}"}
    else:
        print("⚠️ No authentication token found. API calls may fail.")
        return {}

def get_company_data():
    """Get company data from the API"""
    try:
        headers = get_headers()
        response = requests.get(f"{API_URL}/api/companies/{TEST_COMPANY_ID}", headers=headers)
        
        if response.status_code == 200:
            return response.json()
        else:
            print(f"Error getting company: Status code {response.status_code}")
            print(f"Response: {response.text}")
            return None
    except Exception as e:
        print(f"Error getting company data: {e}")
        return None

def update_company():
    """Update the company through the API"""
    try:
        headers = get_headers()
        
        # Convert brand_colors to FormData expected format
        form_data = {
            "name": new_company_data["name"],
            "description": new_company_data["description"]
        }
        
        # Add brand colors as separate form fields
        for i, color in enumerate(new_company_data["brand_colors"]):
            form_data[f"brand_colors[{i}]"] = color
        
        print(f"Updating company with data: {form_data}")
        response = requests.put(f"{API_URL}/api/companies/{TEST_COMPANY_ID}", data=form_data, headers=headers)
        
        if response.status_code == 200:
            return response.json()
        else:
            print(f"Error updating company: Status code {response.status_code}")
            print(f"Response: {response.text}")
            return None
    except Exception as e:
        print(f"Error updating company: {e}")
        return None

def check_database_file():
    """Check if the update was persisted to disk"""
    try:
        if not os.path.exists(DATABASE_PATH):
            print(f"❌ Database file does not exist at {DATABASE_PATH}")
            return None
            
        with open(DATABASE_PATH, 'r') as f:
            db_data = json.load(f)
            
        if TEST_COMPANY_ID not in db_data:
            print(f"❌ Company with ID '{TEST_COMPANY_ID}' not found in database")
            return None
            
        company = db_data[TEST_COMPANY_ID]
        print(f"Company in database: {json.dumps(company, indent=2)}")
        return company
    except Exception as e:
        print(f"❌ Error reading database: {e}")
        return None

def verify_update(before, updated, database):
    """Verify the update was successful and persisted"""
    success = True
    
    # Check name update
    if updated["name"] != new_company_data["name"]:
        print(f"❌ Name not updated correctly: {updated['name']} != {new_company_data['name']}")
        success = False
    else:
        print(f"✅ Name updated correctly: {updated['name']}")
        
    # Check description update
    if updated["description"] != new_company_data["description"]:
        print(f"❌ Description not updated correctly: {updated['description']} != {new_company_data['description']}")
        success = False
    else:
        print(f"✅ Description updated correctly: {updated['description']}")
        
    # Check brand colors update
    updated_colors = updated.get("brand_colors", [])
    if updated_colors != new_company_data["brand_colors"]:
        print(f"❌ Brand colors not updated correctly: {updated_colors} != {new_company_data['brand_colors']}")
        success = False
    else:
        print(f"✅ Brand colors updated correctly: {updated_colors}")
        
    # Check database persistence
    if database and database["name"] == new_company_data["name"]:
        print(f"✅ Name persisted to database")
    else:
        print(f"❌ Name not persisted to database: {database.get('name', 'None')}")
        success = False
        
    # Check database brand colors
    if database and database.get("brand_colors") == new_company_data["brand_colors"]:
        print(f"✅ Brand colors persisted to database")
    else:
        print(f"❌ Brand colors not persisted to database: {database.get('brand_colors', 'None')}")
        success = False
        
    return success
    
def main():
    """Main test function"""
    print("\n" + "="*50)
    print("  COMPANY UPDATE PERSISTENCE TEST")
    print("="*50 + "\n")
    
    # Get current company data
    print("1. Getting current company data...")
    before = get_company_data()
    if before:
        print(f"Current company: {before['name']}")
        print(f"Current brand colors: {before.get('brand_colors', 'None')}")
    else:
        print("❌ Could not get current company data")
        return False
        
    # Update company
    print("\n2. Updating company...")
    updated = update_company()
    if not updated:
        print("❌ Failed to update company")
        return False
        
    # Give the database time to persist changes
    print("\n3. Waiting for changes to persist...")
    time.sleep(1)
    
    # Check database file
    print("\n4. Checking database file...")
    database = check_database_file()
    
    # Verify update
    print("\n5. Verifying update...")
    success = verify_update(before, updated, database)
    
    print("\n" + "="*50)
    if success:
        print("✅✅✅ PERSISTENCE TEST PASSED")
        print("Company updates are correctly persisted to database")
    else:
        print("❌❌❌ PERSISTENCE TEST FAILED")
        print("Some updates were not correctly persisted")
    print("="*50 + "\n")
    
    return success
    
if __name__ == "__main__":
    success = main()
    sys.exit(0 if success else 1)
