#!/usr/bin/env python3
"""
Final verification test for company persistence fix with detailed logging
"""
import sys
import asyncio
import json
from datetime import datetime
import logging

# Configure logging
logging.basicConfig(level=logging.DEBUG, format='%(asctime)s - %(name)s - %(levelname)s - %(message)s')
logger = logging.getLogger("persistence-test")

# Project path
PROJECT_PATH = '/mnt/c/Users/brc07274/OneDrive - Philips/Philips Files/BU - CI/Repository/AI Marketing Agent (Python)/ai-marketing-agent'

async def test_fix():
    print("=== COMPANY PERSISTENCE FIX VERIFICATION (FINAL) ===")
    
    # Import necessary modules
    sys.path.insert(0, PROJECT_PATH)
    from app.db.simple_mock_db import SimpleMockDatabase
    from app.db.company import CompanyDB
    from app.models.company import CompanyUpdate
    
    # Create a mock database
    db = SimpleMockDatabase()
    company_db = CompanyDB(db.companies)
    
    # Step 1: Create a test company
    print("\nStep 1: Creating test company...")
    test_company = {
        "_id": "test_company",
        "name": "Original Company",
        "description": "Original description",
        "email": "original@example.com",
        "brand_colors": ["#000000"],  # Black
        "active": True,
        "created_at": datetime.utcnow(),
        "updated_at": datetime.utcnow()
    }
    
    # Insert directly into database
    await db.companies.insert_one(test_company)
    print("✓ Test company inserted into database")
    
    # Step 2: Verify the company was created
    print("\nStep 2: Verifying company exists...")
    company = await company_db.get_by_string_id("test_company")
    if company:
        print(f"✓ Test company retrieved with name: {company.get('name')}")
        print(f"✓ Initial colors: {company.get('brand_colors')}")
    else:
        print("✗ Failed to retrieve test company")
        return False
    
    # Step 3: Update the company with new colors
    print("\nStep 3: Updating company with new colors...")
    new_colors = ["#FF0000", "#00FF00", "#0000FF"]  # RGB
    update_data = CompanyUpdate(
        name="Updated Company",
        brand_colors=new_colors
    )
    
    # Show exactly what's in the update model
    print(f"Update model data: {update_data.model_dump()}")
    
    # Apply the update
    updated = await company_db.update_company("test_company", update_data)
    if updated:
        print(f"✓ Company updated successfully")
        print(f"✓ New name: {updated.get('name')}")
        print(f"✓ New colors: {updated.get('brand_colors')}")
    else:
        print("✗ Failed to update company")
        return False
    
    # Step 4: Verify the update using a fresh database query
    print("\nStep 4: Verifying persistence with fresh query...")
    
    # Create a new database connection to ensure we're not using any cached data
    new_db = SimpleMockDatabase()
    new_company_db = CompanyDB(new_db.companies)
    
    # Load the test company again
    final = await new_company_db.get_by_string_id("test_company")
    if not final:
        print("✗ Failed to retrieve company after update")
        return False
    
    # Check if the changes persisted
    name_updated = final.get('name') == "Updated Company"
    colors_updated = final.get('brand_colors') == new_colors
    
    print(f"Final company state: {json.dumps(final, default=str)}")
    print(f"Name updated: {'✓' if name_updated else '✗'}")
    print(f"Actual name: '{final.get('name')}', expected: 'Updated Company'")
    print(f"Colors updated: {'✓' if colors_updated else '✗'}")
    print(f"Actual colors: {final.get('brand_colors')}, expected: {new_colors}")
    
    # Overall result
    return name_updated and colors_updated

if __name__ == "__main__":
    try:
        # Run the test
        success = asyncio.run(test_fix())
        
        # Print final result
        print("\n" + "=" * 40)
        if success:
            print("🎉 SUCCESS: Company persistence fix is working!")
            print("Changes to brand_colors are now properly persisted.")
            sys.exit(0)
        else:
            print("❌ FAILED: Company persistence fix is not working.")
            sys.exit(1)
    except Exception as e:
        print(f"\n❌ ERROR: {str(e)}")
        import traceback
        traceback.print_exc()
        sys.exit(1)
