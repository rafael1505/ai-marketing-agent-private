#!/usr/bin/env python3
"""
Verification test for company persistence fix
This script doesn't require the API server to be running
"""
import sys
import asyncio
import json
import logging
from pprint import pformat

# Configure logging with more verbose output
logging.basicConfig(level=logging.DEBUG, 
                    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s')

# Create a logger for this script
logger = logging.getLogger("persistence-test")
logger.setLevel(logging.DEBUG)

# Add console handler for better visibility
console = logging.StreamHandler()
console.setLevel(logging.DEBUG)
formatter = logging.Formatter('%(asctime)s - %(name)s - %(levelname)s - %(message)s')
console.setFormatter(formatter)
logger.addHandler(console)

# Project path
PROJECT_PATH = '/mnt/c/Users/brc07274/OneDrive - Philips/Philips Files/BU - CI/Repository/AI Marketing Agent (Python)/ai-marketing-agent'

async def test_persistence_fix():
    print("=== COMPANY PERSISTENCE FIX VERIFICATION ===")
    
    try:
        # Import necessary modules
        sys.path.insert(0, PROJECT_PATH)
        from app.db.simple_mock_db import SimpleMockDatabase
        from app.db.company import CompanyDB
        from app.models.company import CompanyUpdate
        from datetime import datetime
        
        # Create a mock database and company DB
        db = SimpleMockDatabase()
        company_db = CompanyDB(db.companies)
        
        # Set up a test company
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
        
        # Insert the test company
        await db.companies.insert_one(test_company)
        
        # Verify the company was created
        print("Testing if company exists...")
        company = await company_db.get_by_string_id("test_company")
        if company:
            print(f"✓ Test company created with name: {company.get('name')}")
            print(f"✓ Initial colors: {company.get('brand_colors')}")
        else:
            print("✗ Failed to create test company")
            return False
        
        # Update the company with new colors
        print("\nUpdating company with new colors...")
        new_colors = ["#FF0000", "#00FF00", "#0000FF"]  # RGB
        
        # Debug: Check how brand_colors are represented in the model
        update = CompanyUpdate(
            name="Updated Company",
            brand_colors=new_colors
        )
        print(f"CompanyUpdate object brand_colors: {update.brand_colors}")
        print(f"CompanyUpdate dict representation: {update.model_dump()}")
        
        # Apply the update
        updated = await company_db.update_company("test_company", update)
        if updated:
            print(f"✓ Company updated successfully with name: {updated.get('name')}")
            print(f"✓ Updated colors: {updated.get('brand_colors')}")
        else:
            print("✗ Failed to update company")
            return False
        
        # Verify the update by getting the company again
        print("\nVerifying persistence...")
        final = await company_db.get_by_string_id("test_company")
        if not final:
            print("✗ Failed to retrieve company after update")
            return False
        
        # Dump the entire company object for debugging
        print(f"Final company state: {json.dumps(final, default=str)}")
        
        # Check if the changes persisted
        name_updated = final.get('name') == "Updated Company"
        colors_updated = final.get('brand_colors') == new_colors
        
        print(f"Name updated: {'✓' if name_updated else '✗'}")
        print(f"Actual name: '{final.get('name')}', expected: 'Updated Company'")
        print(f"Colors updated: {'✓' if colors_updated else '✗'}")
        print(f"Actual colors: {final.get('brand_colors')}, expected: {new_colors}")
        
        # Overall result
        success = name_updated and colors_updated
        
        return success
    
    except Exception as e:
        print(f"Error during test: {e}")
        import traceback
        traceback.print_exc()
        return False

if __name__ == "__main__":
    # Run the test
    success = asyncio.run(test_persistence_fix())
    
    # Print final result
    print("\n" + "=" * 40)
    if success:
        print("🎉 SUCCESS: Company persistence fix is working!")
        print("Changes to brand_colors are now properly persisted.")
    else:
        print("❌ FAILED: Company persistence fix is not working.")
    
    sys.exit(0 if success else 1)
