#!/usr/bin/env python3

"""
Direct database test for company persistence issues.
This script:
1. Directly accesses the database (bypassing API)
2. Modifies company data
3. Verifies the changes were persisted
"""

import sys
import os
import time
import asyncio
from datetime import datetime

# Add the project directory to the path to import app modules
sys.path.append(os.path.dirname(os.path.abspath(__file__)))

# Import the necessary modules directly from the app
try:
    from app.models.company import CompanyCreate, CompanyUpdate
    from app.db.company import CompanyDB
    from app.db.simple_mock_db import SimpleMockDatabase
except ImportError as e:
    print(f"Failed to import app modules: {e}")
    sys.exit(1)

async def test_direct_company_persistence():
    print("\n🔍 DIRECT COMPANY DATABASE TEST\n" + "="*30)
    
    # Create simple mock database 
    print("Creating mock database connection...")
    mock_db = SimpleMockDatabase()
    company_db = CompanyDB(mock_db.companies)
    
    # Step 1: Get the current company
    print("\n📋 Step 1: Getting current company from database...")
    try:
        company = await company_db.get_active_company()
        
        # If no company found, create a test company
        if not company:
            print("No active company found, creating test company...")
            test_company = {
                "_id": "test_company",
                "id": "test_company",
                "name": "Test Company",
                "description": "A test company for debugging",
                "brand_colors": [],
                "logo_url": "",
                "active": True,
                "created_at": datetime.utcnow(),
                "updated_at": datetime.utcnow()
            }
            await mock_db.companies.insert_one(test_company)
            company = await company_db.get_active_company()
            
        print(f"Found company: {company.get('name')}")
        print(f"Current colors: {company.get('brand_colors', [])}")
        
    except Exception as e:
        print(f"Error getting company: {str(e)}")
        return False
    
    # Generate unique test values
    timestamp = int(time.time())
    test_name = f"Direct Test Company {timestamp}"
    test_colors = [f"#{timestamp % 1000000:06x}", "#00FF00"]
    
    print(f"\n📋 Step 2: Updating company with test data...")
    print(f"   - Test name: {test_name}")
    print(f"   - Test colors: {test_colors}")
    
    # Create update object
    company_update = CompanyUpdate(
        name=test_name,
        description="Updated via direct database access",
        brand_colors=test_colors
    )
    
    # Update the company
    try:
        updated = await company_db._update_special_company("test_company", company_update.model_dump(exclude_unset=True))
        print(f"Company updated in database: {updated is not None}")
    except Exception as e:
        print(f"Error updating company: {str(e)}")
        return False
    
    # Verify the update
    print("\n📋 Step 3: Verifying data persistence...")
    try:
        updated_company = await mock_db.companies.find_one({"_id": "test_company"})
        
        if not updated_company:
            print("❌ Company not found after update!")
            return False
            
        print(f"Retrieved company: {updated_company.get('name')}")
        print(f"Retrieved colors: {updated_company.get('brand_colors', [])}")
        
        # Check if the update was successful
        name_updated = updated_company.get('name') == test_name
        colors_updated = sorted(updated_company.get('brand_colors', [])) == sorted(test_colors)
        
        print(f"\n🔍 UPDATE VERIFICATION:")
        print(f"   - Name updated: {'✅' if name_updated else '❌'}")
        print(f"   - Colors updated: {'✅' if colors_updated else '❌'}")
        
        if name_updated and colors_updated:
            print("\n✅ SUCCESS: Database updates working correctly!")
            return True
        else:
            print("\n❌ FAILURE: Database updates not applied correctly.")
            return False
            
    except Exception as e:
        print(f"Error verifying update: {str(e)}")
        return False
    
if __name__ == "__main__":
    # Run the async test function
    success = asyncio.run(test_direct_company_persistence())
    sys.exit(0 if success else 1)
