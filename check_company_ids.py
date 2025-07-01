#!/usr/bin/env python3
"""
Script to check and fix company IDs in the database
"""
import asyncio
import json
from datetime import datetime
from motor.motor_asyncio import AsyncIOMotorClient
from bson import ObjectId

# Simple JSON encoder that handles ObjectId and datetime
class MongoJSONEncoder(json.JSONEncoder):
    def default(self, obj):
        if isinstance(obj, ObjectId):
            return str(obj)
        if isinstance(obj, datetime):
            return obj.isoformat()
        return super().default(obj)

async def check_companies():
    """Check all companies in the database and their IDs"""
    print("Connecting to MongoDB...")
    client = AsyncIOMotorClient('mongodb://localhost:27017')
    db = client['ai_marketing_agent']
    
    # Get all companies
    companies = await db.companies.find().to_list(length=100)
    
    print(f"\nFound {len(companies)} companies in the database:")
    print("=" * 50)
    
    for c in companies:
        print(f"ID (_id): {c.get('_id')}")
        print(f"String ID (id): {c.get('id')}")
        print(f"Name: {c.get('name')}")
        print(f"Active: {c.get('active')}")
        print(f"Brand colors: {c.get('brand_colors')}")
        print("-" * 50)
    
    # Check for test_company specifically
    test_company = await db.companies.find_one({"_id": "test_company"})
    test_company_by_id = await db.companies.find_one({"id": "test_company"})
    active_company = await db.companies.find_one({"active": True})
    
    print("\nSpecific checks:")
    print("=" * 50)
    print(f"Company with _id='test_company' exists: {test_company is not None}")
    print(f"Company with id='test_company' exists: {test_company_by_id is not None}")
    print(f"Active company exists: {active_company is not None}")
    
    if active_company:
        print(f"Active company _id: {active_company.get('_id')}")
        print(f"Active company id: {active_company.get('id')}")
    
    return companies, test_company, test_company_by_id, active_company

async def fix_test_company(companies, test_company, test_company_by_id, active_company):
    """Create or fix the test_company if needed"""
    client = AsyncIOMotorClient('mongodb://localhost:27017')
    db = client['ai_marketing_agent']
    
    print("\nFixing company issues...")
    print("=" * 50)
    
    if not active_company:
        print("No active company found. Creating one with id='test_company'...")
        
        new_company = {
            "_id": "test_company",
            "id": "test_company",
            "name": "Test Company",
            "description": "Test company created by fix script",
            "email": "test@example.com",
            "phone": "+1 (555) 123-4567",
            "address": "123 Test Street, Test City, TC 12345",
            "logo_url": "/uploads/default_logo.png",
            "brand_colors": ["#FF0000", "#00FF00", "#0000FF"],
            "active": True,
            "created_at": datetime.utcnow(),
            "updated_at": datetime.utcnow()
        }
        
        await db.companies.insert_one(new_company)
        print("Created new company with id='test_company'")
        
    elif not test_company and not test_company_by_id:
        print("Active company exists but not with id='test_company'. Creating a duplicate with correct ID...")
        
        # Create a copy of the active company with the test_company ID
        active_company_copy = dict(active_company)
        
        # Remove _id so we can insert a new document
        if "_id" in active_company_copy:
            del active_company_copy["_id"]
        
        # Set the proper IDs
        active_company_copy["_id"] = "test_company"
        active_company_copy["id"] = "test_company"
        
        # Insert the new document
        await db.companies.insert_one(active_company_copy)
        print("Created duplicate company with id='test_company'")
        
    elif active_company and active_company.get("_id") != "test_company":
        print("Active company exists but has different ID. Updating active company to have id='test_company'...")
        
        # Create a new document with test_company ID
        active_company_copy = dict(active_company)
        
        # Remove _id so we can insert a new document
        if "_id" in active_company_copy:
            del active_company_copy["_id"]
        
        # Set the proper IDs
        active_company_copy["_id"] = "test_company"
        active_company_copy["id"] = "test_company"
        active_company_copy["updated_at"] = datetime.utcnow()
        
        # Make sure brand_colors is a list
        if "brand_colors" not in active_company_copy or active_company_copy["brand_colors"] is None:
            active_company_copy["brand_colors"] = []
        
        # Delete existing test_company documents if they exist
        await db.companies.delete_many({"$or": [{"_id": "test_company"}, {"id": "test_company"}]})
        
        # Insert the new document
        await db.companies.insert_one(active_company_copy)
        
        # Update the old active company to be inactive
        old_id = active_company.get("_id")
        if old_id and old_id != "test_company":
            await db.companies.update_one({"_id": old_id}, {"$set": {"active": False}})
        
        print("Created new active company with id='test_company'")
    else:
        print("test_company already exists and is active. Making sure IDs are consistent...")
        
        # Make sure both _id and id fields are set to test_company
        await db.companies.update_one(
            {"active": True},
            {"$set": {
                "_id": "test_company", 
                "id": "test_company",
                "updated_at": datetime.utcnow()
            }}
        )
        
        print("Updated test_company to ensure consistent IDs")
    
    # Final check
    final_company = await db.companies.find_one({"_id": "test_company"})
    if final_company:
        print("\nFixed company details:")
        print(f"ID: {final_company.get('_id')}")
        print(f"String ID: {final_company.get('id')}")
        print(f"Name: {final_company.get('name')}")
        print(f"Active: {final_company.get('active')}")
        print(f"Brand colors: {final_company.get('brand_colors')}")
        return True
    else:
        print("\nFailed to fix company!")
        return False

async def main():
    # Check companies
    companies, test_company, test_company_by_id, active_company = await check_companies()
    
    # Fix issues if needed
    if not test_company or not active_company or active_company.get("_id") != "test_company":
        success = await fix_test_company(companies, test_company, test_company_by_id, active_company)
        if success:
            print("\n✅ Company fixed successfully!")
        else:
            print("\n❌ Failed to fix company issues.")
    else:
        print("\n✅ No issues found with test_company!")

if __name__ == "__main__":
    asyncio.run(main())
