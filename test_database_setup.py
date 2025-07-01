#!/usr/bin/env python3
"""
Test script to verify database initialization without starting the server.
"""
import asyncio
from datetime import datetime
from app.db.simple_mock_db import SimpleMockDatabase
from app.db.company import CompanyDB

async def test_database_setup():
    """Test initializing the database with a consistent company."""
    print("=== Testing Database Initialization ===")
    
    # 1. Connect to mock database
    mock_db = SimpleMockDatabase()
    company_db = CompanyDB(mock_db.companies)
    
    # 2. Clear all existing companies
    print("\nClearing existing companies...")
    companies = await mock_db.companies.find({})
    for company in companies:
        await mock_db.companies.delete_one({"_id": company["_id"]})
    print("Database cleared.")
    
    # 3. Create a test company with consistent IDs
    print("\nCreating test company...")
    test_company = {
        "_id": "test_company",        # String ID for direct lookups
        "id": "test_company",         # Consistent ID for API endpoints
        "name": "Test Company",
        "description": "This is a test company for development",
        "email": "contact@testcompany.com",
        "phone": "+1 (555) 123-4567",
        "address": "123 Test Street, Test City, TC 12345",
        "logo_url": "/uploads/default_logo.png",
        "brand_colors": ["#3B82F6", "#A855F7"],
        "active": True,                # Mark as active company
        "created_at": datetime.utcnow(),
        "updated_at": datetime.utcnow()
    }
    
    # Insert the company into the database
    await mock_db.companies.insert_one(test_company)
    print("Test company created successfully with ID: test_company")
    
    # 4. Verify the company exists and is properly configured
    company = await company_db.get_company("test_company")
    if company:
        print("✓ Company verification successful")
        print(f"  Name: {company.get('name')}")
        print(f"  ID: {company.get('id')}")
        print(f"  _ID: {company.get('_id')}")
        print(f"  Active: {company.get('active')}")
        print(f"  Brand Colors: {company.get('brand_colors')}")
        
        # Test updating the company with new brand colors
        print("\nTesting company update...")
        from app.models.company import CompanyUpdate
        
        update = CompanyUpdate(
            name="Updated Test Company",
            description="This company was updated during testing",
            brand_colors=["#FF0000", "#00FF00", "#0000FF"]
        )
        
        updated = await company_db.update_company("test_company", update)
        if updated:
            print("✓ Database update successful")
            print(f"  Updated name: {updated.get('name')}")
            print(f"  Updated colors: {updated.get('brand_colors')}")
            
            # Verify the update persisted
            verify = await company_db.get_company("test_company")
            if verify:
                print("\nVerifying update persisted...")
                name_matches = verify.get('name') == update.name
                colors_match = sorted(verify.get('brand_colors', [])) == sorted(update.brand_colors)
                
                print(f"  Name matches: {'✓' if name_matches else '✗'}")
                print(f"  Colors match: {'✓' if colors_match else '✗'}")
                
                if name_matches and colors_match:
                    print("\n✓ Company persistence is working correctly at database level!")
                    return True
        
        print("✗ Company update verification failed")
        return False
    else:
        print("✗ Failed to verify company in database!")
        return False

if __name__ == "__main__":
    # Run the test function
    success = asyncio.run(test_database_setup())
    if success:
        print("\n🎉 Database test successful! The persistence fix is working correctly.")
    else:
        print("\n❌ Database test failed. Check the errors above.")
