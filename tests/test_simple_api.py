#!/usr/bin/env python3

import asyncio
import sys
import os
sys.path.append(os.path.dirname(os.path.abspath(__file__)))

async def test_mock_db():
    """Test the mock database directly"""
    from app.db.mock_db import MockDatabase
    
    print("Testing MockDatabase...")
    db = MockDatabase()
    
    # Test company creation
    companies = db.companies
    test_company = {
        "id": "test_company",
        "name": "Test Company",
        "active": True
    }
    
    print("Inserting test company...")
    result = await companies.insert_one(test_company)
    print(f"Insert result: {result.inserted_id}")
    
    # Test finding the company
    print("Finding active company...")
    active_company = await companies.find_one({"active": True})
    print(f"Active company: {active_company}")
    
    # Test getting specific company
    company = await companies.find_one({"name": "Test Company"})
    print(f"Test company: {company}")
    
    db.close()
    print("Mock database test completed successfully!")

if __name__ == "__main__":
    asyncio.run(test_mock_db())
