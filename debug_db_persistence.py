#!/usr/bin/env python3
"""
Debug script for company persistence issues
This script performs direct database operations to test the fix
"""

import asyncio
import sys
import os
import json

# Add project root to Python path
sys.path.insert(0, os.path.abspath("."))

async def debug_company_persistence():
    """Test company persistence directly at the database level"""
    try:
        # Import database layer
        from app.db.simple_mock_db import SimpleMockDatabase
        from app.db.company import CompanyDB
        from app.models.company import CompanyUpdate
        from datetime import datetime
        
        print("=== Company Persistence Debug ===")
        print("Testing direct database operations\n")
        
        # Create mock database and company DB
        mock_db = SimpleMockDatabase()
        company_db = CompanyDB(mock_db.companies)
        
        # Get current company
        current_company = await company_db.get_active_company()
        if current_company:
            print(f"Found active company: {current_company.get('name', 'Unknown')}")
            print(f"Current brand_colors: {current_company.get('brand_colors')}")
            company_id = current_company.get("id") or current_company.get("_id")
        else:
            print("No active company found, creating test company")
            test_company = {
                "_id": "test_company",
                "id": "test_company",
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
            await mock_db.companies.insert_one(test_company)
            company_id = "test_company"
            print(f"Created test company with ID: {company_id}")
        
        # Create company update with brand colors
        print("\nUpdating company with new brand colors")
        update_data = CompanyUpdate(
            name="Debug Test Company",
            description="Testing direct DB update",
            brand_colors=["#FF0000", "#00FF00", "#0000FF"]
        )
        
        print(f"Update data: {json.dumps(update_data.model_dump(), indent=2)}")
        
        # Perform the update
        updated_company = await company_db.update_company(company_id, update_data)
        if updated_company:
            print("\nUpdate succeeded!")
            print(f"Updated company: {json.dumps(updated_company, indent=2, default=str)}")
        else:
            print("\nUpdate failed!")
            return False
        
        # Retrieve the company again to verify persistence
        print("\nRetrieving company to verify persistence")
        retrieved_company = await company_db.get_active_company()
        if retrieved_company:
            print(f"Retrieved company: {json.dumps(retrieved_company, indent=2, default=str)}")
            
            # Check if brand_colors persisted
            expected_colors = update_data.brand_colors
            actual_colors = retrieved_company.get("brand_colors", [])
            
            if not actual_colors:
                print("\n❌ FAILURE: No brand_colors found in retrieved company")
                return False
            
            if sorted(actual_colors) == sorted(expected_colors):
                print("\n✅ SUCCESS: Brand colors persisted correctly!")
            else:
                print("\n❌ FAILURE: Brand colors did not persist correctly")
                print(f"Expected: {expected_colors}")
                print(f"Actual: {actual_colors}")
                return False
                
            # Check if name persisted
            if retrieved_company.get("name") == update_data.name:
                print("✅ SUCCESS: Company name persisted correctly!")
                return True
            else:
                print("❌ FAILURE: Company name did not persist correctly")
                print(f"Expected: {update_data.name}")
                print(f"Actual: {retrieved_company.get('name')}")
                return False
        else:
            print("\n❌ FAILURE: Could not retrieve company after update")
            return False
            
    except Exception as e:
        print(f"\n❌ ERROR: {e}")
        import traceback
        traceback.print_exc()
        return False

if __name__ == "__main__":
    result = asyncio.run(debug_company_persistence())
    print("\n===============================")
    if result:
        print("✅ Database layer test PASSED")
    else:
        print("❌ Database layer test FAILED")
