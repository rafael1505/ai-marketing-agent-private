#!/usr/bin/env python3
"""
Direct database test for company persistence issue without API dependency
"""
import sys
import asyncio
import json
from datetime import datetime

# Project path
PROJECT_PATH = '/mnt/c/Users/brc07274/OneDrive - Philips/Philips Files/BU - CI/Repository/AI Marketing Agent (Python)/ai-marketing-agent'
sys.path.insert(0, PROJECT_PATH)

# Direct imports (no try/except to see errors clearly)
from app.db.simple_mock_db import SimpleMockDatabase
from app.models.company import CompanyUpdate

async def main():
    print("=== DIRECT DB PERSISTENCE TEST ===")
    
    # Create test database
    db = SimpleMockDatabase()
    
    # Create test company
    test_company = {
        "_id": "test_company",
        "name": "Original Company",
        "brand_colors": ["#000000"],
        "active": True,
        "created_at": datetime.utcnow(),
        "updated_at": datetime.utcnow()
    }
    
    # Insert company
    await db.companies.insert_one(test_company)
    print("Company created")
    
    # Get company to verify
    company = await db.companies.find_one({"_id": "test_company"})
    print(f"Initial company: {company}")
    
    # Update with new colors directly
    new_colors = ["#FF0000", "#00FF00", "#0000FF"]
    update_result = await db.companies.update_one(
        {"_id": "test_company"},
        {"$set": {"brand_colors": new_colors}}
    )
    print(f"Update result: {update_result.matched_count} matched, {update_result.modified_count} modified")
    
    # Get updated company
    updated = await db.companies.find_one({"_id": "test_company"})
    print(f"Updated company: {updated}")
    print(f"Colors match: {updated.get('brand_colors') == new_colors}")

if __name__ == "__main__":
    asyncio.run(main())
