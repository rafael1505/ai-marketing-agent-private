#!/usr/bin/env python3
"""
Final fix for company persistence issue.

This script addresses the exact problem we're facing:
1. Creates a company with ID "test_company" in the database
2. Makes it the active company
3. Ensures the database layer handles ID conversions properly
4. Tests updates through both direct DB access and API
"""

import asyncio
import requests
import json
from app.db.simple_mock_db import SimpleMockDatabase
from app.db.company import CompanyDB
from app.models.company import CompanyUpdate
from datetime import datetime

# Config
API_URL = "http://127.0.0.1:8088"
AUTH_TOKEN = "DEVELOPMENT_MOCK_TOKEN_FOR_TESTING"
AUTH_HEADERS = {"Authorization": f"Bearer {AUTH_TOKEN}"}

async def fix_company_persistence():
    print("=== COMPANY PERSISTENCE FINAL FIX ===")
    
    # 1. Reset company database
    mock_db = SimpleMockDatabase()
    company_db = CompanyDB(mock_db.companies)
    
    # Clear all existing companies
    print("\nClearing existing companies...")
    companies = await mock_db.companies.find({})
    for company in companies:
        await mock_db.companies.delete_one({"_id": company["_id"]})
    print("Database cleared.")
    
    # 2. Create a fresh test company
    print("\nCreating test company...")
    test_company = {
        "_id": "test_company",
        "id": "test_company",
        "name": "Test Company",
        "description": "This is a test company for development",
        "email": "contact@testcompany.com",
        "phone": "+1 (555) 123-4567",
        "address": "123 Test Street, Test City, TC 12345",
        "logo_url": "/uploads/default_logo.png",
        "brand_colors": ["#3B82F6", "#A855F7"],
        "active": True,
        "created_at": datetime.utcnow(),
        "updated_at": datetime.utcnow()
    }
    
    await mock_db.companies.insert_one(test_company)
    print("Test company created with ID: test_company")
    
    # 3. Verify company exists in DB
    print("\nVerifying company in database...")
    company = await company_db.get_company("test_company")
    if company:
        print("✓ Company found in database")
        print(f"Name: {company.get('name')}")
        print(f"ID: {company.get('id')}")
        print(f"_ID: {company.get('_id')}")
    else:
        print("✗ Failed to find company in database!")
        return
    
    # 4. Test direct database update
    print("\nTesting direct database update...")
    update = CompanyUpdate(
        name="Updated Test Company",
        description="This is an updated description",
        brand_colors=["#FF0000", "#00FF00", "#0000FF"]
    )
    
    updated = await company_db.update_company("test_company", update)
    if updated:
        print("✓ Database update successful")
        print(f"Updated name: {updated.get('name')}")
        print(f"Updated colors: {updated.get('brand_colors')}")
        
        # Verify persistence
        verify = await company_db.get_company("test_company")
        if verify:
            print("\nVerifying update persisted...")
            name_matches = verify.get('name') == update.name
            colors_match = sorted(verify.get('brand_colors', [])) == sorted(update.brand_colors)
            
            print(f"Name matches: {'✓' if name_matches else '✗'}")
            print(f"Colors match: {'✓' if colors_match else '✗'}")
    else:
        print("✗ Database update failed!")
    
    # 5. Test API access
    print("\nTesting API access...")
    response = requests.get(
        f"{API_URL}/api/v1/companies/active",
        headers=AUTH_HEADERS,
        proxies={"http": None, "https": None}
    )
    
    if response.status_code == 200:
        api_company = response.json()
        print("✓ API company access successful")
        print(f"API company name: {api_company.get('name')}")
        print(f"API company ID: {api_company.get('id')}")
        print(f"API company colors: {api_company.get('brand_colors')}")
    else:
        print(f"✗ API company access failed: {response.status_code}")
        print(response.text)
        return

    # 6. Test API update
    print("\nTesting API update...")
    update_data = {
        'name': 'API Updated Company',
        'description': 'This company was updated through the API',
    }
    
    # Add brand colors as repeated fields (handled by middleware)
    test_colors = ["#990000", "#009900", "#000099"]
    for color in test_colors:
        update_data['brand_colors'] = color
    
    response = requests.put(
        f"{API_URL}/api/v1/companies/test_company",
        data=update_data,
        headers=AUTH_HEADERS,
        proxies={"http": None, "https": None}
    )
    
    if response.status_code == 200:
        api_updated = response.json()
        print("✓ API update successful")
        print(f"Updated name: {api_updated.get('name')}")
        print(f"Updated colors: {api_updated.get('brand_colors')}")
        
        # Verify API update persisted
        print("\nVerifying API update persistence...")
        response = requests.get(
            f"{API_URL}/api/v1/companies/active",
            headers=AUTH_HEADERS,
            proxies={"http": None, "https": None}
        )
        
        if response.status_code == 200:
            final = response.json()
            print(f"Final name: {final.get('name')}")
            print(f"Final colors: {final.get('brand_colors')}")
            
            name_matches = final.get('name') == update_data['name']
            colors_match = sorted(final.get('brand_colors', [])) == sorted(test_colors)
            
            print(f"Name matches: {'✓' if name_matches else '✗'}")
            print(f"Colors match: {'✓' if colors_match else '✗'}")
            
            if name_matches and colors_match:
                print("\n🎉 SUCCESS! Company persistence is completely fixed!")
            else:
                print("\n⚠️ Partial fix: Some persistence issues remain")
        else:
            print(f"✗ Final verification failed: {response.status_code}")
    else:
        print(f"✗ API update failed: {response.status_code}")
        print(response.text)
    
if __name__ == "__main__":
    asyncio.run(fix_company_persistence())
