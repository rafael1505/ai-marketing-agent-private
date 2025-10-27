#!/usr/bin/env python3
"""
Script to fix company data persistence issues by diagnosing and repairing the data format.
This script directly interacts with the database to ensure proper data structure and format.
"""

import asyncio
import os
import json
import shutil
from datetime import datetime

# Import necessary modules
from app.db.simple_mock_db import SimpleMockDatabase
from app.db.company import CompanyDB

async def fix_company_data():
    print("=== COMPANY DATA PERSISTENCE FIX ===\n")
    
    # Initialize database
    mock_db = SimpleMockDatabase()
    company_db = CompanyDB(mock_db.companies)
    
    # Get active company
    active_company = await company_db.get_active_company()
    
    if not active_company:
        print("❌ No active company found!")
        await create_test_company(company_db, mock_db)
        active_company = await company_db.get_active_company()
        if not active_company:
            print("❌ Failed to create active company!")
            return False
    
    print(f"Found active company: {active_company.get('name')}")
    print(f"ID: {active_company.get('id')}, _id: {active_company.get('_id')}")
    
    # Check and fix IDs
    await fix_company_ids(active_company, company_db, mock_db)
    
    # Fix brand colors
    await fix_brand_colors(active_company, company_db, mock_db)
    
    # Fix logo URL
    await fix_logo_url(active_company, company_db, mock_db)
    
    # Verify fixes
    await verify_fixes(company_db)
    
    print("\n=== FIX COMPLETE ===")
    return True

async def create_test_company(company_db, mock_db):
    """Create a test company if none exists"""
    print("Creating test company...")
    test_company = {
        "name": "Test Company",
        "description": "This is a test company for development",
        "email": "contact@testcompany.com", 
        "phone": "+1 (555) 123-4567",
        "address": "123 Test Street, Test City, TC 12345",
        "logo_url": "/uploads/default_logo.png",
        "brand_colors": ["#3B82F6", "#A855F7"],
        "active": True,
        "_id": "test_company",
        "id": "test_company",
        "created_at": datetime.utcnow(),
        "updated_at": datetime.utcnow(),
    }
    
    await mock_db.companies.insert_one(test_company)
    print("✅ Test company created successfully")

async def fix_company_ids(company, company_db, mock_db):
    """Fix inconsistent company IDs"""
    print("\nChecking company IDs...")
    
    company_id = company.get('id') or company.get('_id') or 'test_company'
    
    if not company.get('_id') or company.get('_id') != company_id:
        print(f"⚠️  Inconsistent _id found. Setting _id = '{company_id}'")
        try:
            # Create fixed document
            fixed_company = {
                **company,
                "_id": company_id,
                "id": company_id
            }
            
            # Delete old document
            if company.get('_id'):
                await mock_db.companies.delete_one({"_id": company.get('_id')})
            elif company.get('id'):
                await mock_db.companies.delete_one({"id": company.get('id')})
            
            # Insert fixed document
            await mock_db.companies.insert_one(fixed_company)
            print("✅ Company ID fixed")
        except Exception as e:
            print(f"❌ Error fixing company ID: {e}")
    else:
        print("✓ Company IDs are consistent")

async def fix_brand_colors(company, company_db, mock_db):
    """Fix brand colors array"""
    print("\nFixing brand colors...")
    
    brand_colors = company.get('brand_colors')
    
    if not brand_colors:
        print("⚠️  Missing brand_colors. Setting defaults...")
        brand_colors = ["#3B82F6", "#A855F7"]  # Default blue and purple
    elif not isinstance(brand_colors, list):
        print(f"⚠️  Invalid brand_colors format: {type(brand_colors)}. Converting to list...")
        try:
            brand_colors = list(brand_colors)
        except:
            brand_colors = ["#3B82F6", "#A855F7"]
    
    # Filter out empty values
    brand_colors = [color for color in brand_colors if color]
    
    # Ensure we have at least one color
    if not brand_colors:
        brand_colors = ["#3B82F6"]
    
    print(f"Setting brand_colors to: {brand_colors}")
    
    # Update brand_colors directly
    company_id = company.get('id') or company.get('_id')
    try:
        await mock_db.companies.update_one(
            {"_id": company_id},
            {"$set": {"brand_colors": brand_colors}}
        )
        print("✅ Brand colors fixed")
    except Exception as e:
        print(f"❌ Error fixing brand colors: {e}")

async def fix_logo_url(company, company_db, mock_db):
    """Fix logo URL if it's a blob or invalid"""
    print("\nFixing logo URL...")
    
    logo_url = company.get('logo_url', '')
    
    if not logo_url:
        print("⚠️  Missing logo_url. Setting default...")
        logo_url = "/uploads/default_logo.png"
    elif logo_url.startswith('blob:'):
        print(f"⚠️  Found blob URL: {logo_url}. Replacing with default...")
        logo_url = "/uploads/default_logo.png"
    
    # Update logo_url directly
    company_id = company.get('id') or company.get('_id')
    try:
        await mock_db.companies.update_one(
            {"_id": company_id},
            {"$set": {"logo_url": logo_url}}
        )
        print("✅ Logo URL fixed")
    except Exception as e:
        print(f"❌ Error fixing logo URL: {e}")

async def verify_fixes(company_db):
    """Verify that all fixes were applied correctly"""
    print("\nVerifying fixes...")
    
    company = await company_db.get_active_company()
    
    if not company:
        print("❌ No active company found after fixes!")
        return False
    
    print(f"Company name: {company.get('name')}")
    print(f"ID: {company.get('id')}, _id: {company.get('_id')}")
    
    # Check brand_colors
    brand_colors = company.get('brand_colors', [])
    if isinstance(brand_colors, list) and len(brand_colors) > 0:
        print(f"✓ Brand colors: {brand_colors}")
    else:
        print(f"❌ Brand colors are still invalid: {brand_colors}")
    
    # Check logo_url
    logo_url = company.get('logo_url', '')
    if logo_url and not logo_url.startswith('blob:'):
        print(f"✓ Logo URL: {logo_url}")
    else:
        print(f"❌ Logo URL is still invalid: {logo_url}")
    
    return True

if __name__ == "__main__":
    asyncio.run(fix_company_data())
