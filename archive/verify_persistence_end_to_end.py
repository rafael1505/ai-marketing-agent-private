#!/usr/bin/env python3
"""
Verify Company Persistence End-to-End Test

This script tests the full persistence flow:
1. Update company information
2. Verify the update was successful
3. Check that changes are stored in the database file
4. Suggest restarting the API server to verify persistence
"""

import requests
import json
import os
import datetime
import time
import sys
import subprocess

API_URL = "http://localhost:8088"
TEST_COMPANY_ID = "test_company"
DATABASE_PATH = "app/db/data/companies.json"

# Authentication token path
AUTH_TOKEN_FILE = "auth_token.json"

# New company data for testing
new_company_data = {
    "name": f"Updated Test Company {datetime.datetime.now().strftime('%H:%M:%S')}",
    "description": "This company was updated by the persistence test",
    "logo_url": "/uploads/test_logo.png",
    "brand_colors": ["#FF5733", "#33FF57", "#3357FF", "#F3FF33", "#FF33F3"]
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

def get_company_data(company_id=TEST_COMPANY_ID):
    """Get company data from the API"""
    try:
        headers = get_headers()
        response = requests.get(f"{API_URL}/api/companies/{company_id}", headers=headers)
        response.raise_for_status()
        return response.json()
    except Exception as e:
        print(f"Error getting company data: {e}")
        if 'response' in locals():
            print(f"Response status: {response.status_code}")
            print(f"Response content: {response.text}")
        return None

def check_database_file():
    """Check if the database file exists and contains the test company"""
    db_path = os.path.join(os.path.dirname(os.path.abspath(__file__)), DATABASE_PATH)
    print(f"Checking database file at {db_path}")
    
    if not os.path.exists(db_path):
        print("❌ Database file does not exist!")
        return None
    
    try:
        with open(db_path, 'r') as f:
            db_data = json.load(f)
            print(f"Database content: {json.dumps(db_data, indent=2)}")
            
            # Search for our company by the test company ID
            found_company = None
            for company_id, company_data in db_data.items():
                if company_data.get("_id") == TEST_COMPANY_ID:
                    found_company = company_data
                    break
                    
            return found_company
    except Exception as e:
        print(f"Error reading database file: {e}")
        return None

def update_company(company_id=TEST_COMPANY_ID):
    """Update the company with new data"""
    try:
        # Convert brand_colors to FormData expected format
        form_data = {
            "name": new_company_data["name"],
            "description": new_company_data["description"],
            "logo_url": new_company_data["logo_url"]
        }
        
        # Add brand colors as separate form fields
        for i, color in enumerate(new_company_data["brand_colors"]):
            form_data[f"brand_colors[{i}]"] = color
        
        print(f"Updating company with data: {form_data}")
        headers = get_headers()
        response = requests.put(f"{API_URL}/api/companies/{company_id}", data=form_data, headers=headers)
        response.raise_for_status()
        return response.json()
    except Exception as e:
        print(f"Error updating company: {e}")
        if 'response' in locals():
            print(f"Response status: {response.status_code}")
            print(f"Response content: {response.text}")
        return None

def main():
    """Main test function"""
    print("\n" + "="*50)
    print("COMPANY PERSISTENCE END-TO-END TEST")
    print("="*50)
    
    print("\n1. Getting current company data...")
    original_company = get_company_data()
    if original_company:
        print(f"Current company data: {json.dumps(original_company, indent=2)}")
    else:
        print("❌ Failed to get company data. Make sure the API server is running.")
        return False
    
    print("\n2. Updating company with new data...")
    updated_company = update_company()
    if updated_company:
        print(f"✅ Company updated successfully: {json.dumps(updated_company, indent=2)}")
    else:
        print("❌ Failed to update company")
        return False
    
    print("\n3. Verifying update with API...")
    verified_company = get_company_data()
    if verified_company:
        print(f"Company data after update: {json.dumps(verified_company, indent=2)}")
        
        # Check if update was successful
        success = True
        if verified_company.get("name") != new_company_data["name"]:
            print(f"❌ Name mismatch: {verified_company.get('name')} != {new_company_data['name']}")
            success = False
            
        if verified_company.get("description") != new_company_data["description"]:
            print(f"❌ Description mismatch: {verified_company.get('description')} != {new_company_data['description']}")
            success = False
            
        # Check brand colors
        api_colors = verified_company.get("brand_colors", [])
        if not api_colors or api_colors != new_company_data["brand_colors"]:
            print(f"❌ Brand colors mismatch: {api_colors} != {new_company_data['brand_colors']}")
            success = False
            
        if success:
            print("✅ All company data was updated correctly in the API")
        else:
            print("❌ Some company data was not updated correctly")
    else:
        print("❌ Failed to verify company update")
        return False
    
    print("\n4. Checking database file...")
    db_company = check_database_file()
    if db_company:
        print("✅ Company found in database file")
        
        # Check if database entry matches API data
        db_success = True
        if db_company.get("name") != verified_company.get("name"):
            print(f"❌ Database name mismatch: {db_company.get('name')} != {verified_company.get('name')}")
            db_success = False
            
        db_colors = db_company.get("brand_colors", [])
        api_colors = verified_company.get("brand_colors", [])
        if db_colors != api_colors:
            print(f"❌ Database brand colors mismatch: {db_colors} != {api_colors}")
            db_success = False
        
        if db_success:
            print("✅ Database file matches API data")
        else:
            print("⚠️ Database file contains differences from API data")
    else:
        print("❌ Company not found in database file")
    
    print("\n" + "="*50)
    print("TEST RESULTS:")
    if db_company and success:
        print("✅ First phase complete: Company updates are saved to database file")
        
        print("\n5. To verify persistence across API restarts:")
        print("   a. Stop the API server (Ctrl+C in the terminal running the API)")
        print("   b. Start the API server again (run the 'Run API (Mock Database)' task)")
        print("   c. Run this script again with --verify flag to verify persisted data")
        
        if len(sys.argv) > 1 and sys.argv[1] == "--verify":
            print("\nVerification phase started!")
            verified_company = get_company_data()
            if verified_company:
                print(f"Company data after API restart: {json.dumps(verified_company, indent=2)}")
                
                # Check if data persisted
                persisted = True
                if verified_company.get("name") != new_company_data["name"]:
                    print(f"❌ Name did not persist: {verified_company.get('name')} != {new_company_data['name']}")
                    persisted = False
                    
                if verified_company.get("description") != new_company_data["description"]:
                    print(f"❌ Description did not persist: {verified_company.get('description')} != {new_company_data['description']}")
                    persisted = False
                    
                # Check brand colors
                api_colors = verified_company.get("brand_colors", [])
                if not api_colors or api_colors != new_company_data["brand_colors"]:
                    print(f"❌ Brand colors did not persist: {api_colors} != {new_company_data['brand_colors']}")
                    persisted = False
                    
                if persisted:
                    print("\n✅✅✅ PERSISTENCE TEST PASSED: All company data persisted after API restart!")
                    return True
                else:
                    print("\n❌ PERSISTENCE TEST FAILED: Company data did not persist correctly after API restart")
                    return False
            else:
                print("❌ Failed to get company data after API restart")
                return False
        
        return True
    else:
        print("❌ TEST FAILED: Company updates not saved correctly")
        return False

if __name__ == "__main__":
    success = main()
    sys.exit(0 if success else 1)
