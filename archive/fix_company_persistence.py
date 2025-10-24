"""
Company persistence fix script - directly fixes the company data in the database
"""
import asyncio
import os
import sys
from motor.motor_asyncio import AsyncIOMotorClient
from datetime import datetime

# Constants
DATABASE_URI = "mongodb://localhost:27017"  # default MongoDB URI
DATABASE_NAME = "ai_marketing_agent"
COMPANY_ID = "test_company"

async def fix_company_persistence():
    """Fix company persistence issues by directly updating the MongoDB database"""
    print("Fixing company persistence issues...")
    
    # Connect to MongoDB
    client = AsyncIOMotorClient(DATABASE_URI)
    db = client[DATABASE_NAME]
    companies_collection = db.companies
    
    # Check for existing company
    print("Checking for existing company...")
    company = await companies_collection.find_one({"active": True})
    
    if not company:
        print("No active company found. Creating one...")
        new_company = {
            "_id": COMPANY_ID,
            "id": COMPANY_ID,
            "name": "Philips",
            "description": "This is a test company",
            "email": "test@example.com", 
            "logo_url": "/uploads/default_logo.png",
            "brand_colors": ["#FF0000", "#00FF00", "#0000FF"],
            "active": True,
            "created_at": datetime.utcnow(),
            "updated_at": datetime.utcnow()
        }
        await companies_collection.insert_one(new_company)
        print("Created new company.")
        return
    
    # Fix existing company
    print(f"Found company: {company.get('name')}")
    
    # Ensure both _id and id fields exist and match
    has_id = "id" in company
    has_underscore_id = "_id" in company
    id_matches = has_id and has_underscore_id and company["_id"] == company["id"]
    
    print(f"Company has 'id': {has_id}")
    print(f"Company has '_id': {has_underscore_id}")
    print(f"ID fields match: {id_matches}")
    
    # If we need to fix ID fields, create a new document
    if not id_matches or not has_id or not has_underscore_id:
        print("Fixing company ID fields...")
        
        # Create fixed company with both _id and id set to test_company
        fixed_company = {**company}
        # Remove _id so we can insert a new one
        if "_id" in fixed_company:
            del fixed_company["_id"]
            
        fixed_company["id"] = COMPANY_ID
        fixed_company["_id"] = COMPANY_ID
        
        # Make sure brand_colors is a list
        if "brand_colors" not in fixed_company or fixed_company["brand_colors"] is None:
            fixed_company["brand_colors"] = []
        
        # Delete existing company
        print("Removing old company document...")
        await companies_collection.delete_many({"active": True})
        
        # Insert fixed company
        print("Inserting fixed company document...")
        await companies_collection.insert_one(fixed_company)
    else:
        # Update brand_colors directly
        print("Updating brand_colors to ensure they persist...")
        current_colors = company.get("brand_colors", [])
        if current_colors is None:
            current_colors = []
            
        print(f"Current brand_colors: {current_colors}")
        
        # Add a timestamp to easily see when it was last updated
        timestamp_color = f"#20{datetime.now().strftime('%y%m%d%H%M%S')}"
        
        # Update with current colors plus timestamp
        new_colors = list(current_colors) if isinstance(current_colors, list) else []
        if timestamp_color not in new_colors:
            new_colors.append(timestamp_color)
        
        print(f"New brand_colors: {new_colors}")
        
        await companies_collection.update_one(
            {"active": True},
            {"$set": {
                "brand_colors": new_colors,
                "updated_at": datetime.utcnow()
            }}
        )
    
    # Verify fix
    updated_company = await companies_collection.find_one({"active": True})
    print("\nVerification:")
    print(f"Company name: {updated_company.get('name')}")
    print(f"Company _id: {updated_company.get('_id')}")
    print(f"Company id: {updated_company.get('id')}")
    print(f"Brand colors: {updated_company.get('brand_colors')}")
    
    print("\n✅ Company persistence fix applied successfully!")
    
# Main function
async def main():
    await fix_company_persistence()

if __name__ == "__main__":
    # Run the async main function
    asyncio.run(main())
