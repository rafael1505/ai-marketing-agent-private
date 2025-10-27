#!/usr/bin/env python3
# filepath: /mnt/c/Users/brc07274/OneDrive - Philips/Philips Files/BU - CI/Repository/AI Marketing Agent (Python)/ai-marketing-agent/list_companies.py
import sys
import os
import json
import asyncio
from pathlib import Path

# Add the project root to the Python path to enable importing app modules
sys.path.append(str(Path(__file__).parent))

from app.db.simple_mock_db import SimpleMockDatabase
from app.db.company import CompanyDB

async def list_all_companies():
    """List all companies in the database"""
    print("Connecting to database...")
    db = SimpleMockDatabase()
    company_db = CompanyDB(db.companies)
    
    print("\nAll companies in database:")
    
    # Try to get the active company
    active_company = await db.companies.find_one({"active": True})
    if active_company:
        print("\n--- Active Company ---")
        print(f"ID (_id): {active_company.get('_id')}")
        print(f"ID (id): {active_company.get('id')}")
        print(f"Name: {active_company.get('name')}")
        print(f"Brand Colors: {active_company.get('brand_colors')}")
        print(f"\nFull data: {json.dumps(active_company, default=str, indent=2)}")
    else:
        print("No active company found!")
    
    # Try to directly get test_company
    test_company = await company_db.get_by_string_id("test_company")
    if test_company:
        print("\n--- Test Company ---")
        print(f"ID (_id): {test_company.get('_id')}")
        print(f"ID (id): {test_company.get('id')}")
        print(f"Name: {test_company.get('name')}")
        print(f"Brand Colors: {test_company.get('brand_colors')}")
        print(f"\nFull data: {json.dumps(test_company, default=str, indent=2)}")
    else:
        print("\nNo 'test_company' found directly!")
    
    # List all companies
    companies = []
    cursor = db.companies.find({})
    async for doc in cursor:
        companies.append(doc)
    
    if not companies:
        print("\nNo companies found in the database!")
        return
    
    print(f"\n--- All Companies ({len(companies)}) ---")
    for idx, company in enumerate(companies):
        print(f"\n--- Company {idx + 1} ---")
        print(f"ID (_id): {company.get('_id')}")
        print(f"ID (id): {company.get('id')}")
        print(f"Name: {company.get('name')}")
        print(f"Active: {company.get('active')}")
        print(f"Brand Colors: {company.get('brand_colors')}")

if __name__ == "__main__":
    asyncio.run(list_all_companies())
