#!/usr/bin/env python3

import asyncio
import sys
import os
import requests
import json

# Add the project root to the Python path
sys.path.insert(0, '/mnt/c/Users/brc07274/OneDrive - Philips/Philips Files/BU - CI/Repository/AI Marketing Agent (Python)/ai-marketing-agent')

async def test_company_persistence():
    print("=== Testing Company Persistence Issue ===\n")
    
    try:
        from app.db.simple_mock_db import SimpleMockDatabase
        from app.db.company import CompanyDB
        from datetime import datetime
        
        # Create mock database and company DB
        mock_db = SimpleMockDatabase()
        company_db = CompanyDB(mock_db.companies)
        
        print("1. Database setup complete")
        
        # First, check what's currently in the database
        print("\n2. Checking current database state...")
        all_companies = await mock_db.companies.find()
        print(f"All companies in DB: {all_companies}")
        
        active_company = await company_db.get_active_company()
        print(f"Active company: {active_company}")
        
        # If no company exists, create a test company
        if not active_company:
            print("\n3. Creating test company...")
            test_company = {
                "_id": "test_company",
                "name": "Test Company",
                "description": "This is a test company for development",
                "email": "contact@testcompany.com",
                "logo_url": "/uploads/default-logo.png",
                "brand_colors": ["#3B82F6", "#A855F7"],
                "active": True,
                "created_at": datetime.utcnow(),
                "updated_at": datetime.utcnow()
            }
            
            # Insert directly into the collection
            result = await mock_db.companies.insert_one(test_company)
            print(f"Insert result: {result.inserted_id}")
            
            active_company = await company_db.get_active_company()
            print(f"New active company: {active_company}")
        
        # Now test the update and retrieval process
        print("\n4. Testing company update...")
        
        from app.models.company import CompanyUpdate
        
        # Create an update
        update_data = CompanyUpdate(
            name="Updated Test Company",
            description="This company has been updated!",
            brand_colors=["#FF0000", "#00FF00", "#0000FF"]
        )
        
        print(f"Updating company with data: {update_data.model_dump()}")
        
        # Perform the update
        updated_company = await company_db.update_company("test_company", update_data)
        print(f"Update result: {updated_company}")
        
        # Retrieve the company again to see if changes persisted
        print("\n5. Checking if update persisted...")
        retrieved_company = await company_db.get_active_company()
        print(f"Retrieved company after update: {retrieved_company}")
        
        # Check by string ID as well
        retrieved_by_id = await company_db.get_by_string_id("test_company")
        print(f"Retrieved by string ID: {retrieved_by_id}")
        
        # Compare the data
        if retrieved_company and updated_company:
            print("\n6. Comparison results:")
            print(f"Name matches: {retrieved_company.get('name') == updated_company.get('name')}")
            print(f"Description matches: {retrieved_company.get('description') == updated_company.get('description')}")
            print(f"Colors match: {retrieved_company.get('brand_colors') == updated_company.get('brand_colors')}")
        
        return True
        
    except Exception as e:
        print(f"Error during testing: {e}")
        import traceback
        traceback.print_exc()
        return False

def test_api_endpoints():
    print("\n=== Testing API Endpoints ===\n")
    
    base_url = "http://127.0.0.1:8088"
    
    # Test 1: Get active company
    print("1. Testing GET /api/v1/companies/active")
    try:
        response = requests.get(f"{base_url}/api/v1/companies/active")
        print(f"Status: {response.status_code}")
        if response.status_code == 200:
            company_data = response.json()
            print(f"Company data: {json.dumps(company_data, indent=2)}")
        else:
            print(f"Error response: {response.text}")
    except requests.exceptions.RequestException as e:
        print(f"Request failed: {e}")
    
    print("\n" + "="*50 + "\n")

if __name__ == "__main__":
    print("Starting persistence debug script...")
    try:
        # Test the database layer
        db_result = asyncio.run(test_company_persistence())
        
        # Test the API layer
        test_api_endpoints()
        
        print(f"\nDatabase test result: {'PASSED' if db_result else 'FAILED'}")
    except Exception as e:
        print(f"Error in main: {e}")
        import traceback
        traceback.print_exc()
