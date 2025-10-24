#!/usr/bin/env python3
"""
Minimal test focusing solely on the company database layer
"""

import asyncio
from datetime import datetime
import sys
import os

# Add the project root to the Python path
sys.path.insert(0, '/mnt/c/Users/brc07274/OneDrive - Philips/Philips Files/BU - CI/Repository/AI Marketing Agent (Python)/ai-marketing-agent')

async def test_direct_db_persistence():
    print("Testing direct database persistence...")
    try:
        # Import database classes
        from app.db.simple_mock_db import SimpleMockDatabase
        from app.db.company import CompanyDB
        from app.models.company import CompanyUpdate
        
        # Create database instances
        db = SimpleMockDatabase()
        company_db = CompanyDB(db.companies)
        
        # Check for existing company or create one
        existing_company = await company_db.get_by_string_id("test_company")
        
        if not existing_company:
            print("Creating test company...")
            test_company = {
                "_id": "test_company",
                "name": "Original Test Company",
                "description": "Test description",
                "brand_colors": ["#000000"],
                "active": True,
                "created_at": datetime.utcnow(),
                "updated_at": datetime.utcnow()
            }
            await db.companies.insert_one(test_company)
            print("Test company created.")
        
        # Check current state
        before = await company_db.get_by_string_id("test_company")
        print(f"Before update - Name: {before.get('name')}, Colors: {before.get('brand_colors', [])}")
        
        # Create update
        update_data = CompanyUpdate(
            name="Updated Test Company",
            description="Updated description",
            brand_colors=["#FF0000", "#00FF00", "#0000FF"]
        )
        
        # Perform update
        print("Updating company...")
        updated = await company_db.update_company("test_company", update_data)
        print(f"Update result - Name: {updated.get('name')}, Colors: {updated.get('brand_colors', [])}")
        
        # Verify changes by getting the company again
        after = await company_db.get_by_string_id("test_company")
        print(f"After update - Name: {after.get('name')}, Colors: {after.get('brand_colors', [])}")
        
        # Check if changes persisted
        name_updated = after.get('name') == "Updated Test Company"
        colors_updated = after.get('brand_colors') == ["#FF0000", "#00FF00", "#0000FF"]
        
        print(f"Name updated: {'✅ YES' if name_updated else '❌ NO'}")
        print(f"Colors updated: {'✅ YES' if colors_updated else '❌ NO'}")
        
        if name_updated and colors_updated:
            print("✅ SUCCESS: Database changes are persisting correctly!")
            return True
        else:
            print("❌ FAILED: Database changes are not persisting correctly.")
            return False
            
    except Exception as e:
        print(f"❌ ERROR: {e}")
        import traceback
        traceback.print_exc()
        return False

if __name__ == "__main__":
    print("=== Direct Database Persistence Test ===\n")
    success = asyncio.run(test_direct_db_persistence())
    exit(0 if success else 1)
