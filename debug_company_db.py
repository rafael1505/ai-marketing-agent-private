#!/usr/bin/env python3

import asyncio
import sys
import os

# Add the project root to the Python path
sys.path.insert(0, '/mnt/c/Users/brc07274/OneDrive - Philips/Philips Files/BU - CI/Repository/AI Marketing Agent (Python)/ai-marketing-agent')

async def test_company_db():
    print("Starting company DB test...")
    
    try:
        from app.db.simple_mock_db import SimpleMockDatabase
        print("Imported SimpleMockDatabase")
        
        from app.db.company import CompanyDB
        print("Imported CompanyDB")
        
        from datetime import datetime
        print("Imported datetime")
        
        # Create mock database
        mock_db = SimpleMockDatabase()
        print("Created mock database")
        
        company_db = CompanyDB(mock_db.companies)
        print("Created company DB")
        
        # Create test company data
        test_company = {
            "id": "test_company",
            "name": "Test Company",
            "description": "This is a test company for development",
            "email": "contact@testcompany.com",
            "active": True
        }
        print(f"Created test company data: {test_company}")
        
        # Insert directly into the collection
        result = await mock_db.companies.insert_one(test_company)
        print(f"Insert result: {result.inserted_id}")
        
        # Check what's in the database
        all_companies = await mock_db.companies.find()
        print(f"All companies: {all_companies}")
        
        # Try to get active company
        active_company = await company_db.get_active_company()
        print(f"Active company: {active_company}")
        
    except Exception as e:
        print(f"Error: {e}")
        import traceback
        traceback.print_exc()

if __name__ == "__main__":
    asyncio.run(test_company_db())
