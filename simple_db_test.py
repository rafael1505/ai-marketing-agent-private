#!/usr/bin/env python3
"""
Simple direct test for company persistence focusing just on the database layer
"""
import asyncio
import sys

async def test_db_layer():
    try:
        from app.db.simple_mock_db import SimpleMockDatabase
        from app.db.company import CompanyDB
        from app.models.company import CompanyUpdate
        from datetime import datetime
        
        print("Creating mock database...")
        db = SimpleMockDatabase()
        company_db = CompanyDB(db.companies)
        
        # Create a test company if it doesn't exist
        test_company = {
            "_id": "test_company",
            "name": "Original Test Company",
            "description": "Testing company persistence",
            "brand_colors": ["#000000"],  # Black
            "active": True,
            "created_at": datetime.utcnow(),
            "updated_at": datetime.utcnow()
        }
        
        print("Inserting test company...")
        await db.companies.insert_one(test_company)
        
        # Verify the company exists
        print("Verifying company exists...")
        company = await company_db.get_by_string_id("test_company")
        print(f"Initial company state: {company}")
        
        # Create update with new colors
        print("\nUpdating company with new colors...")
        update = CompanyUpdate(
            name="Updated Company Name",
            brand_colors=["#FF0000", "#00FF00", "#0000FF"]  # RGB
        )
        
        # Apply the update
        updated = await company_db.update_company("test_company", update)
        print(f"Update result: {updated}")
        
        # Verify the update
        print("\nVerifying update...")
        final = await company_db.get_by_string_id("test_company")
        print(f"Final company state: {final}")
        
        # Check if colors were updated
        expected_colors = ["#FF0000", "#00FF00", "#0000FF"]
        actual_colors = final.get('brand_colors', []) if final else []
        success = actual_colors == expected_colors
        
        print(f"\nColors updated correctly: {success}")
        print(f"Expected: {expected_colors}")
        print(f"Actual: {actual_colors}")
        
        return success
        
    except Exception as e:
        print(f"Error in test_db_layer: {e}")
        import traceback
        traceback.print_exc()
        return False

if __name__ == "__main__":
    print("=== SIMPLE COMPANY DATABASE TEST ===\n")
    
    try:
        # Add the project root to Python path
        sys.path.append('/mnt/c/Users/brc07274/OneDrive - Philips/Philips Files/BU - CI/Repository/AI Marketing Agent (Python)/ai-marketing-agent')
        
        # Run the test
        success = asyncio.run(test_db_layer())
        
        # Print result
        if success:
            print("\n✅ SUCCESS: The database layer is working correctly!")
        else:
            print("\n❌ FAILED: The database layer is not working correctly.")
        
        sys.exit(0 if success else 1)
        
    except Exception as e:
        print(f"Error in main: {e}")
        import traceback
        traceback.print_exc()
        sys.exit(1)
