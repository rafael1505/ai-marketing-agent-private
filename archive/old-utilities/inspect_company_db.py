#!/usr/bin/env python3
"""
Script to directly inspect the company database collection
to help diagnose the persistence issues.
"""

import asyncio
from app.db.company import CompanyDB
from app.db.simple_mock_db import SimpleMockDatabase
import json

async def inspect_companies():
    print("Connecting to mock database...")
    # Create a simple mock database instance
    mock_db = SimpleMockDatabase()
    company_db = CompanyDB(mock_db.companies)
    
    # Get all companies
    print("Getting all companies in database:")
    all_companies = await mock_db.companies.find({})
    if not all_companies:
        print("No companies found in database.")
        return
    
    print(f"Found {len(all_companies)} companies:")
    for idx, company in enumerate(all_companies, 1):
        # Format _id for display
        id_value = str(company.get("_id", "None"))
        
        print(f"\nCompany #{idx}:")
        print(f"  _id: {id_value}")
        print(f"  id: {company.get('id', 'None')}")
        print(f"  name: {company.get('name', 'None')}")
        print(f"  active: {company.get('active', False)}")
        print(f"  brand_colors: {company.get('brand_colors', [])} (type: {type(company.get('brand_colors', [])).__name__})")
    
    # Try to get the active company
    print("\nGetting active company:")
    active_company = await company_db.get_active_company()
    if active_company:
        print(f"Active company found: {active_company.get('name')} (ID: {active_company.get('_id')}, string ID: {active_company.get('id')})")
    else:
        print("No active company found!")
    
    # Try to directly access test_company
    print("\nTrying to get test_company by ID:")
    test_company = await company_db.get_company("test_company")
    if test_company:
        print(f"test_company found: {test_company.get('name')} (ID: {test_company.get('_id')})")
    else:
        print("test_company not found in database!")
    
    # Try to get company with ID "2"
    print("\nTrying to get company with ID '2':")
    company_2 = await company_db.get_company("2")
    if company_2:
        print(f"Company with ID 2 found: {company_2.get('name')} (ID: {company_2.get('_id')})")
    else:
        print("Company with ID 2 not found in database!")
    
    # Try to get string ID vs ObjectId handling
    print("\nID handling test:")
    print(f"Is '2' a valid ObjectId? {await is_valid_object_id('2')}")
    print(f"Is 'test_company' a valid ObjectId? {await is_valid_object_id('test_company')}")

async def is_valid_object_id(id_str):
    from bson import ObjectId
    try:
        return ObjectId.is_valid(id_str)
    except:
        return False

if __name__ == "__main__":
    asyncio.run(inspect_companies())
