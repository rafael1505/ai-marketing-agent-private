#!/usr/bin/env python3
"""
Focused database test for company persistence issue
"""
import asyncio
import json
import sys
import logging
from pprint import pprint, pformat
from datetime import datetime

# Configure detailed logging
logging.basicConfig(level=logging.DEBUG, 
                   format='%(asctime)s - %(name)s - %(levelname)s - %(message)s')

logger = logging.getLogger("db-test")

# Project path
PROJECT_PATH = '/mnt/c/Users/brc07274/OneDrive - Philips/Philips Files/BU - CI/Repository/AI Marketing Agent (Python)/ai-marketing-agent'

async def test_db_operations():
    """Test focused on direct database operations"""
    print("=== COMPANY DB OPERATIONS TEST ===")
    
    try:
        # Import necessary modules
        sys.path.insert(0, PROJECT_PATH)
        from app.db.simple_mock_db import SimpleMockCollection, SimpleMockDatabase
        
        # Create a simple database for testing
        print("\n1. Creating test database...")
        db = SimpleMockDatabase()
        
        # Define test company data
        test_company = {
            "_id": "test_company",
            "name": "Original Company",
            "brand_colors": ["#000000"],
            "active": True,
            "created_at": datetime.utcnow(),
            "updated_at": datetime.utcnow()
        }
        
        # Test direct database operations
        print("\n2. Testing insert operation...")
        result = await db.companies.insert_one(test_company)
        print(f"Insert result: {result.inserted_id}")
        
        # Verify company exists
        print("\n3. Verifying company was inserted...")
        company = await db.companies.find_one({"_id": "test_company"})
        print(f"Initial company state: {json.dumps(company, default=str)}")
        if not company:
            print("❌ FAILED: Could not retrieve company after insert")
            return False
            
        # Test direct update operation with brand_colors
        print("\n4. Testing direct update with brand_colors...")
        new_colors = ["#FF0000", "#00FF00", "#0000FF"]
        update_data = {
            "$set": {
                "name": "Updated Company",
                "brand_colors": new_colors,
                "updated_at": datetime.utcnow()
            }
        }
        update_result = await db.companies.update_one({"_id": "test_company"}, update_data)
        print(f"Update result: matched={update_result.matched_count}, modified={update_result.modified_count}")
        
        # Verify changes persisted
        print("\n5. Verifying changes persisted...")
        updated_company = await db.companies.find_one({"_id": "test_company"})
        print(f"Updated company state: {json.dumps(updated_company, default=str)}")
        
        # Check results
        if not updated_company:
            print("❌ FAILED: Could not retrieve company after update")
            return False
            
        name_updated = updated_company.get('name') == "Updated Company"
        colors_updated = updated_company.get('brand_colors') == new_colors
        
        print(f"Name updated: {'✓' if name_updated else '❌'}")
        print(f"Actual name: '{updated_company.get('name')}', expected: 'Updated Company'")
        print(f"Colors updated: {'✓' if colors_updated else '❌'}")
        print(f"Actual colors: {updated_company.get('brand_colors')}, expected: {new_colors}")
        
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
    success = asyncio.run(test_db_operations())
    
    # Print final result
    print("\n" + "=" * 40)
    if success:
        print("✅ SUCCESS: Database operations working properly")
    else:
        print("❌ FAILED: Database operations issue detected")
    
    sys.exit(0 if success else 1)
