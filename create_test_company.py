#!/usr/bin/env python3
"""
Script to initialize test company in the database
Also serves as a diagnostic tool for company persistence issues
"""

import asyncio
import os
from datetime import datetime
from app.db.company import CompanyDB
from app.db.simple_mock_db import SimpleMockDatabase
from app.models.company import CompanyCreate, CompanyUpdate

async def create_test_company():
    print("Connecting to mock database...")
    # Create a simple mock database instance
    mock_db = SimpleMockDatabase()
    company_db = CompanyDB(mock_db.companies)
    
    # Step 1: Show all current companies
    print("Current companies in database:")
    companies = await mock_db.companies.find({})
    for idx, company in enumerate(companies):
        print(f"  Company {idx+1}: {company.get('name')} (ID: {company.get('_id')})")
    
    # Step 2: Check if test_company already exists
    test_company = await company_db.get_by_string_id("test_company")
    active_company = await company_db.get_active_company()
    
    if test_company:
        print(f"\nTest company already exists: {test_company.get('name')} (ID: {test_company.get('_id')})")
        print(f"Brand colors: {test_company.get('brand_colors')}")
        
        # Update the company with new data to confirm persistence works
        print("\nUpdating test company with new brand colors...")
        
        random_suffix = os.urandom(2).hex()  # Generate random hex suffix
        update_data = CompanyUpdate(
            name=f"UPDATED Test Company {random_suffix}",
            description="This company was updated by the fix script",
            brand_colors=["#FF5533", "#33FF55", "#5533FF"]  # Distinctive colors
        )
        
        updated_company = await company_db.update_company("test_company", update_data)
        if updated_company:
            print(f"Company updated successfully:")
            print(f"  Name: {updated_company.get('name')}")
            print(f"  Colors: {updated_company.get('brand_colors')}")
        else:
            print("Failed to update test company!")
    elif active_company:
        print(f"\nActive company exists but not with test_company ID: {active_company.get('name')} (ID: {active_company.get('_id')})")
        print("Creating a separate test_company ID...")
        
        # Create a new test company with the proper ID
        test_company_data = {
            "_id": "test_company",
            "id": "test_company",
            "name": "Test Company",
            "description": "This is a test company for development",
            "email": "contact@testcompany.com",
            "phone": "+1 (555) 123-4567",
            "address": "123 Test Street, Test City, TC 12345",
            "logo_url": "/uploads/default_logo.png",
            "brand_colors": ["#1a73e8", "#ea4335", "#fbbc04", "#34a853", "#ffffff"],
            "active": True,
            "created_at": datetime.utcnow(),
            "updated_at": datetime.utcnow()
        }
        
        # Directly insert with the string ID
        await mock_db.companies.insert_one(test_company_data)
    else:
        print("\nNo companies found. Creating test_company...")
        
        # Create a new test company with the proper ID
        test_company = {
            "_id": "test_company", 
            "id": "test_company",
            "name": "Test Company",
            "description": "This is a test company for development",
            "email": "contact@testcompany.com",
            "phone": "+1 (555) 123-4567",
            "address": "123 Test Street, Test City, TC 12345",
            "logo_url": "/uploads/default_logo.png",
            "brand_colors": ["#1a73e8", "#ea4335", "#fbbc04", "#34a853", "#ffffff"],
            "active": True,
            "created_at": datetime.utcnow(),
            "updated_at": datetime.utcnow()
        }
    
        
        # Directly insert with the string ID
        await mock_db.companies.insert_one(test_company)
    
    # Step 3: Verify current state after changes
    print("\nVerifying current database state:")
    
    # Get all companies
    all_companies = await mock_db.companies.find({})
    print(f"\nAll companies in database ({len(all_companies)}):")
    for idx, company in enumerate(all_companies):
        print(f"  Company {idx+1}: {company.get('name')} (ID: {company.get('_id')})")
        print(f"    Active: {company.get('active')}")
        print(f"    Brand colors: {company.get('brand_colors')}")
    
    # Get test_company specifically
    verified_company = await company_db.get_by_string_id("test_company")
    if verified_company:
        print(f"\nTest company verification:")
        print(f"  _id: {verified_company.get('_id')}")
        print(f"  id: {verified_company.get('id')}")
        print(f"  name: {verified_company.get('name')}")
        print(f"  brand_colors: {verified_company.get('brand_colors')}")
        print(f"  active: {verified_company.get('active')}")
    else:
        print("Failed to retrieve test company after creation/update!")
        
    print("\n==== PERSISTENCE FIX INSTRUCTIONS ====")
    print("1. The company data is stored in memory in SimpleMockDatabase")
    print("2. To persist changes between API restarts, you need to:")
    print("   - Run this script after each API server restart")
    print("   - OR modify the application to use a real database like MongoDB")
    print("   - OR enhance SimpleMockDatabase to write data to disk")
    print("3. The data persistence issue is due to in-memory storage")
    print("   being wiped when the API server restarts")
    
if __name__ == "__main__":
    asyncio.run(create_test_company())
