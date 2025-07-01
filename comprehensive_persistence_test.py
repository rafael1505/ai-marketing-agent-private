#!/usr/bin/env python3
"""
Final company persistence test focusing on ID handling and brand colors
"""

import asyncio
import requests
import json
import sys
import os

# Add project directory to Python path
sys.path.append(os.path.abspath('.'))

# Import necessary modules
from app.models.company import CompanyUpdate
from app.db.simple_mock_db import SimpleMockDatabase
from app.db.company import CompanyDB

# Test config
API_BASE_URL = "http://127.0.0.1:8088"
AUTH_HEADER = {"Authorization": "Bearer DEVELOPMENT_MOCK_TOKEN_FOR_TESTING"}

# Test colors
TEST_COLORS = ["#AA0000", "#00AA00", "#0000AA"]

async def test_company_persistence():
    print("=== COMPREHENSIVE COMPANY PERSISTENCE TEST ===\n")
    
    # PART 1: Direct database setup and testing
    print("PART 1: DIRECT DATABASE TESTING")
    print("--------------------------------")
    
    # Create a test company with ID "test_company" directly in DB
    mock_db = SimpleMockDatabase()
    company_db = CompanyDB(mock_db.companies)
    
    # Ensure we have a test company with consistent ID
    await setup_test_company(company_db, mock_db)
    
    # Test updating via direct DB access
    await test_direct_db_update(company_db)
    
    # PART 2: API testing
    print("\nPART 2: API TESTING")
    print("-------------------")
    
    # Test updating via API
    test_api_update()
    
    print("\n=== TEST COMPLETE ===")

async def setup_test_company(company_db, mock_db):
    """Ensure we have a test company with ID 'test_company'"""
    print("Setting up test company...")
    
    # First check for active company
    active_company = await company_db.get_active_company()
    
    if active_company:
        print(f"Found active company: {active_company.get('name')}")
        print(f"ID: {active_company.get('id')}, _id: {active_company.get('_id')}")
        
        # Update it to ensure active=true and id=test_company
        update_result = await mock_db.companies.update_one(
            {"_id": active_company.get('_id')},
            {"$set": {
                "id": "test_company",
                "active": True
            }}
        )
        print(f"Updated active company: matched={update_result.matched_count}")
        
        return True
    
    # No active company found, create a new one
    print("Creating new test_company...")
    # Create a new test company with string ID
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
        "id": "test_company"
    }
    
    # Insert directly into collection
    await mock_db.companies.insert_one(test_company)
    
    # Verify creation
    company = await company_db.get_company("test_company")
    if company:
        print("Test company created successfully")
        print(f"ID: {company.get('id')}, _id: {company.get('_id')}")
    else:
        print("Failed to create test company!")
        return False
    
    return True

async def test_direct_db_update(company_db):
    """Test updating company with direct DB access"""
    print("\nTesting direct database update...")
    
    # Create an update
    update = CompanyUpdate(
        name="DB Updated Company",
        description="Updated via direct database access",
        brand_colors=TEST_COLORS
    )
    
    # Perform the update
    updated = await company_db.update_company("test_company", update)
    
    if not updated:
        print("❌ Direct DB update failed!")
        return False
    
    print("✅ Direct DB update successful")
    print(f"Updated name: {updated.get('name')}")
    print(f"Updated colors: {updated.get('brand_colors', [])}")
    
    # Verify persistence
    company = await company_db.get_company("test_company")
    if not company:
        print("❌ Failed to retrieve company after update!")
        return False
    
    print("\nVerifying persistence...")
    name_matches = company.get('name') == update.name
    colors_match = sorted(company.get('brand_colors', [])) == sorted(update.brand_colors)
    
    print(f"Name matches: {'✓' if name_matches else '✗'} ('{company.get('name')}' vs '{update.name}')")
    print(f"Colors match: {'✓' if colors_match else '✗'}")
    if not colors_match:
        print(f"  Actual: {company.get('brand_colors', [])}")
        print(f"  Expected: {update.brand_colors}")
    
    return name_matches and colors_match

def test_api_update():
    """Test updating company via the API"""
    print("\nTesting API update...")
    
    # Get the test company
    print("Getting test company via API...")
    response = requests.get(
        f"{API_BASE_URL}/api/v1/companies/test_company",
        headers=AUTH_HEADER,
        proxies={"http": None, "https": None}
    )
    
    if response.status_code != 200:
        print(f"❌ Failed to get test company: {response.status_code}")
        print(response.text)
        return False
    
    company = response.json()
    print(f"Company found: {company.get('name')}")
    print(f"ID: {company.get('id')}, _id: {company.get('_id', 'N/A')}")
    
    # Create update data
    print("\nUpdating company via API...")
    update_data = {
        'name': 'API Updated Company',
        'description': 'Updated via API request'
    }
    
    # Add brand colors as repeated fields
    for color in TEST_COLORS:
        update_data['brand_colors'] = color
    
    # Send update request
    response = requests.put(
        f"{API_BASE_URL}/api/v1/companies/test_company",
        data=update_data,
        headers=AUTH_HEADER,
        proxies={"http": None, "https": None}
    )
    
    if response.status_code != 200:
        print(f"❌ API update failed: {response.status_code}")
        print(response.text)
        return False
    
    updated = response.json()
    print("✅ API update successful")
    print(f"Updated name: {updated.get('name')}")
    print(f"Updated colors: {updated.get('brand_colors', [])}")
    
    # Verify persistence
    print("\nVerifying API update persistence...")
    response = requests.get(
        f"{API_BASE_URL}/api/v1/companies/test_company",
        headers=AUTH_HEADER,
        proxies={"http": None, "https": None}
    )
    
    if response.status_code != 200:
        print(f"❌ Failed to get updated company: {response.status_code}")
        print(response.text)
        return False
    
    final = response.json()
    name_matches = final.get('name') == update_data['name']
    colors_match = sorted(final.get('brand_colors', [])) == sorted(TEST_COLORS)
    
    print(f"Name matches: {'✓' if name_matches else '✗'} ('{final.get('name')}' vs '{update_data['name']}')")
    print(f"Colors match: {'✓' if colors_match else '✗'}")
    if not colors_match:
        print(f"  Actual: {final.get('brand_colors', [])}")
        print(f"  Expected: {TEST_COLORS}")
    
    if name_matches and colors_match:
        print("\n🎉 API UPDATE PERSISTENCE CONFIRMED!")
    else:
        print("\n⚠️ API UPDATE PERSISTENCE FAILED!")
    
    return name_matches and colors_match

if __name__ == "__main__":
    asyncio.run(test_company_persistence())
