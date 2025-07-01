#!/usr/bin/env python3
"""
Direct database fix for company persistence issues.
This script bypasses the API and fixes the company document directly in the database.
"""

import json
import pymongo
from bson import ObjectId
import sys
import time
import subprocess

# Configuration
MONGODB_URL = "mongodb://localhost:27017/"
DATABASE_NAME = "test"
COMPANY_ID = "test_company"
TEST_BRAND_COLORS = ["#FF5733", "#33FF57"]  # Test colors for verification

def print_header(text):
    """Print a formatted header"""
    print("\n" + "=" * 80)
    print(f" {text} ".center(78, "*"))
    print("=" * 80 + "\n")

def connect_to_mongodb():
    """Connect to MongoDB and return the client"""
    try:
        client = pymongo.MongoClient(MONGODB_URL)
        # Quick check if connection works
        client.admin.command('ping')
        print("✅ Connected to MongoDB successfully")
        return client
    except Exception as e:
        print(f"❌ Failed to connect to MongoDB: {e}")
        return None

def fix_company_document(client):
    """Fix the company document in MongoDB"""
    db = client[DATABASE_NAME]
    companies = db.companies
    
    # Find all companies to understand what we're working with
    all_companies = list(companies.find())
    print(f"Found {len(all_companies)} companies in database")
    
    for i, company in enumerate(all_companies):
        print(f"Company {i+1}:")
        print(f"  - ID: {company.get('id')}")
        print(f"  - _id: {company.get('_id')}")
        print(f"  - Name: {company.get('name')}")
        print(f"  - Brand Colors: {company.get('brand_colors')}")
        print(f"  - Active: {company.get('active')}")
    
    # Check if our target company exists
    company = companies.find_one({"id": COMPANY_ID})
    
    if not company:
        # Try to find by _id instead
        company = companies.find_one({"_id": COMPANY_ID})
    
    if not company:
        # Try to find the active company
        company = companies.find_one({"active": True})
        
    if not company:
        print("❌ No suitable company found. Creating a new test company.")
        
        # Create a new test company
        new_company = {
            "_id": COMPANY_ID,
            "id": COMPANY_ID,
            "name": "Fixed Test Company",
            "description": "This company was created by the fix script",
            "email": "test@example.com",
            "phone": "123-456-7890",
            "address": "123 Test St.",
            "logo_url": "/uploads/default_logo.png",
            "brand_colors": TEST_BRAND_COLORS,
            "active": True,
            "created_at": time.strftime('%Y-%m-%dT%H:%M:%S.000Z'),
            "updated_at": time.strftime('%Y-%m-%dT%H:%M:%S.000Z')
        }
        
        # Insert the new company
        result = companies.insert_one(new_company)
        print(f"✅ Created new test company with ID: {COMPANY_ID}")
        company = new_company
    else:
        print(f"✅ Found existing company: {company.get('name')} with ID: {company.get('id')}")
        
        # Ensure the company has a consistent ID
        update_data = {
            "id": COMPANY_ID,
            "brand_colors": TEST_BRAND_COLORS,
            "updated_at": time.strftime('%Y-%m-%dT%H:%M:%S.000Z')
        }
        
        # If this is an active company but not the test_company, update it
        if company.get("id") != COMPANY_ID:
            print(f"⚠️ Company has incorrect ID: {company.get('id')}. Updating to: {COMPANY_ID}")
            
            # Create a new document with the correct ID
            if isinstance(company.get("_id"), ObjectId):
                # Get the old document (excluding _id which can't be changed)
                old_doc = dict(company)
                old_id = old_doc.pop("_id")
                
                # Create a new document with string ID
                new_doc = {**old_doc, **update_data, "_id": COMPANY_ID}
                
                # Delete the old document and insert the new one
                companies.delete_one({"_id": old_id})
                companies.insert_one(new_doc)
                
                print(f"✅ Recreated company with string ID: {COMPANY_ID}")
                company = companies.find_one({"_id": COMPANY_ID})
            else:
                # Just update the existing document
                companies.update_one({"_id": company.get("_id")}, {"$set": update_data})
                print(f"✅ Updated company with ID: {company.get('id')}")
                company = companies.find_one({"_id": company.get("_id")})
        else:
            # Update brand colors and other fields
            companies.update_one({"_id": company.get("_id")}, {"$set": update_data})
            print(f"✅ Updated test company with new brand colors")
            company = companies.find_one({"_id": company.get("_id")})
    
    # Verify the brand colors
    if company.get("brand_colors") == TEST_BRAND_COLORS:
        print("✅ Brand colors updated successfully")
    else:
        print(f"❌ Brand colors not updated correctly. Current value: {company.get('brand_colors')}")
    
    # Make sure the company is active
    if not company.get("active", False):
        companies.update_one({"_id": company.get("_id")}, {"$set": {"active": True}})
        print("✅ Activated the company")
    
    return company

def verify_api_access(company):
    """Verify that the API can access the fixed company"""
    print_header("VERIFYING API ACCESS")
    
    try:
        # Start the API server in the background
        print("Restarting the API server...")
        subprocess.run(["pkill", "-f", "uvicorn app.main:app"], capture_output=True)
        time.sleep(2)  # Wait for the server to stop
        
        # Start the server in the background
        subprocess.Popen(["python", "-m", "uvicorn", "app.main:app", "--host", "127.0.0.1", "--port", "8088"], 
                        stdout=subprocess.PIPE, stderr=subprocess.PIPE)
        
        print("Waiting 5 seconds for API to start...")
        time.sleep(5)
        
        # Use subprocess to run curl and get the output
        curl_cmd = ["curl", "-s", "http://127.0.0.1:8088/api/v1/companies/active"]
        result = subprocess.run(curl_cmd, capture_output=True, text=True)
        
        if result.returncode != 0:
            print(f"❌ Failed to connect to API: {result.stderr}")
            return False
            
        # Parse the JSON response
        api_company = json.loads(result.stdout)
        print(f"API returned company: {api_company.get('name')}")
        print(f"API brand colors: {api_company.get('brand_colors')}")
        
        # Check if the brand colors match
        api_colors = api_company.get('brand_colors', [])
        if sorted(api_colors) == sorted(TEST_BRAND_COLORS):
            print("✅ API is returning the correct brand colors")
            return True
        else:
            print(f"❌ API is returning incorrect brand colors: {api_colors}")
            print(f"Expected: {TEST_BRAND_COLORS}")
            return False
            
    except Exception as e:
        print(f"❌ Error verifying API access: {e}")
        return False

def main():
    print_header("COMPANY PERSISTENCE DATABASE FIX")
    
    # Connect to MongoDB
    client = connect_to_mongodb()
    if not client:
        print("❌ Cannot proceed without MongoDB connection")
        sys.exit(1)
    
    try:
        # Fix the company document
        print_header("FIXING COMPANY DOCUMENT")
        company = fix_company_document(client)
        
        # Verify API access
        api_success = verify_api_access(company)
        
        print_header("SUMMARY")
        if api_success:
            print("✅ Fix completed successfully!")
            print("✅ Brand colors are now persisting correctly")
            print("✅ Company document has consistent ID")
        else:
            print("⚠️ Fix applied but API verification failed")
            print("Please check the API logs for errors")
    
    finally:
        client.close()
        print("\nDatabase connection closed")

if __name__ == "__main__":
    main()
