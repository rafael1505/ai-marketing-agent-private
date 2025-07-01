#!/usr/bin/env python3
"""
Direct Database Fix Script

This script bypasses the database API layer and directly modifies 
the in-memory database to ensure company data is properly structured.
"""

import asyncio
from datetime import datetime

# Import app modules
from app.db.simple_mock_db import SimpleMockDatabase

async def main():
    print("=== Direct Database Fix ===")
    
    # Get direct access to the database
    db = SimpleMockDatabase()
    print("\nRaw database contents before fix:")
    for id_key, company_data in db._data["companies"].items():
        print(f"ID: {id_key}, Name: {company_data.get('name', 'Unknown')}")
    
    # Clear existing companies in the raw dictionary
    db._data["companies"] = {}
    
    # Create a fresh test_company with proper IDs
    test_company = {
        "name": "Test Company",
        "description": "This is a test company for development",
        "email": "contact@testcompany.com",
        "phone": "+1 (555) 123-4567",
        "address": "123 Test Street, Test City, TC 12345",
        "logo_url": "/uploads/default_logo.png",
        "brand_colors": ["#3B82F6", "#A855F7"],
        "active": True,
        "created_at": datetime.utcnow(),
        "updated_at": datetime.utcnow()
    }
    
    # Insert directly into the data dictionary with the correct key
    db._data["companies"]["test_company"] = test_company
    
    print("\nRaw database contents after fix:")
    for id_key, company_data in db._data["companies"].items():
        print(f"ID: {id_key}, Name: {company_data.get('name', 'Unknown')}")
        print(f"  Fields: {list(company_data.keys())}")
        print(f"  Brand colors: {company_data.get('brand_colors')}")
    
    print("\n✅ Direct database fix completed!")
    print("The test_company has been properly created in the database.")

if __name__ == "__main__":
    asyncio.run(main())
