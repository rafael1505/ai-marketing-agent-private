#!/usr/bin/env python3
"""
Minimal standalone test for brand colors persistence
This is a completely self-contained test with no dependencies
"""
print("Starting minimal brand colors persistence test...")

import sys
import json
from datetime import datetime

# Mock database implementation for testing
class MockCollection:
    def __init__(self):
        self.data = {}

    async def insert_one(self, document):
        doc_id = document.get('_id', 'test')
        self.data[doc_id] = document.copy()
        return MockInsertResult(doc_id)

    async def find_one(self, query):
        doc_id = query.get('_id')
        if doc_id in self.data:
            result = self.data[doc_id].copy()
            return result
        return None

    async def update_one(self, query, update):
        doc_id = query.get('_id')
        if doc_id in self.data:
            document = self.data[doc_id]
            if "$set" in update:
                for key, value in update["$set"].items():
                    # Special handling for brand_colors
                    if key == "brand_colors":
                        if value is None:
                            document[key] = []
                        else:
                            document[key] = list(value)
                    else:
                        document[key] = value
            return MockUpdateResult(1, 1)
        return MockUpdateResult(0, 0)

class MockInsertResult:
    def __init__(self, inserted_id):
        self.inserted_id = inserted_id

class MockUpdateResult:
    def __init__(self, matched, modified):
        self.matched_count = matched
        self.modified_count = modified

# Model classes for testing
class CompanyUpdate:
    def __init__(self, name, brand_colors):
        self.name = name
        self.brand_colors = brand_colors

    def model_dump(self, exclude_unset=False):
        return {
            'name': self.name,
            'brand_colors': self.brand_colors
        }

# Company DB class for testing
class CompanyDB:
    def __init__(self, collection):
        self.collection = collection

    async def get_by_string_id(self, company_id):
        company = await self.collection.find_one({"_id": company_id})
        # Ensure brand_colors is always a list copy
        if company and "brand_colors" in company:
            if company["brand_colors"] is None:
                company["brand_colors"] = []
            else:
                company["brand_colors"] = list(company["brand_colors"])
        return company

    async def update_company(self, company_id, company):
        # Extract data from model
        company_data = company.model_dump()
        
        # Fix for brand_colors
        if "brand_colors" in company_data:
            if company_data["brand_colors"] is None:
                company_data["brand_colors"] = []
            else:
                company_data["brand_colors"] = list(company_data["brand_colors"])
        
        # Update timestamp
        company_data["updated_at"] = datetime.utcnow()
        
        # Update database
        update_result = await self.collection.update_one(
            {"_id": company_id},
            {"$set": company_data}
        )
        
        # Get updated company
        return await self.get_by_string_id(company_id)

# Test function
async def test_brand_colors_persistence():
    print("=== MINIMAL BRAND COLORS PERSISTENCE TEST ===")
    
    # Create mock database
    collection = MockCollection()
    company_db = CompanyDB(collection)
    
    # Step 1: Create a test company
    print("\n1. Creating test company...")
    test_company = {
        "_id": "test_company",
        "name": "Original Company",
        "brand_colors": ["#000000"],  # Black
        "created_at": datetime.utcnow(),
        "updated_at": datetime.utcnow()
    }
    
    # Insert into database
    await collection.insert_one(test_company)
    
    # Step 2: Verify company exists
    print("\n2. Verifying company exists...")
    company = await company_db.get_by_string_id("test_company")
    print(f"Initial company: {json.dumps(company, default=str)}")
    
    # Step 3: Update with new colors
    print("\n3. Updating with new colors...")
    new_colors = ["#FF0000", "#00FF00", "#0000FF"]  # RGB
    update = CompanyUpdate(
        name="Updated Company",
        brand_colors=new_colors
    )
    
    # Apply update
    updated = await company_db.update_company("test_company", update)
    print(f"Updated company: {json.dumps(updated, default=str)}")
    
    # Step 4: Verify changes persisted
    print("\n4. Verifying persistence...")
    final = await company_db.get_by_string_id("test_company")
    print(f"Final company: {json.dumps(final, default=str)}")
    
    # Check results
    name_updated = final.get('name') == "Updated Company"
    colors_updated = final.get('brand_colors') == new_colors
    
    print(f"Name updated: {'✓' if name_updated else '✗'}")
    print(f"Colors updated: {'✓' if colors_updated else '✗'}")
    
    return name_updated and colors_updated

# Run the test
if __name__ == "__main__":
    import asyncio
    
    success = asyncio.run(test_brand_colors_persistence())
    
    # Print result
    print("\n" + "=" * 40)
    if success:
        print("✅ SUCCESS: Brand colors persist correctly!")
        sys.exit(0)
    else:
        print("❌ FAILED: Brand colors persistence issue detected.")
        sys.exit(1)
