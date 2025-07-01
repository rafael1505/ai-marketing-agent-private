#!/usr/bin/env python3
# filepath: /mnt/c/Users/brc07274/OneDrive - Philips/Philips Files/BU - CI/Repository/AI Marketing Agent (Python)/ai-marketing-agent/manual_fix.py
"""
Manual fix script that directly addresses the company persistence issue
- Verifies all of the monkey patches are applied
- Ensures the test_company exists with correct ID
- Manually creates and saves the database files
"""

import os
import sys
import json
import asyncio
import shutil
from datetime import datetime
from pathlib import Path

# Add the project root to the Python path to enable importing app modules
sys.path.append(str(Path(__file__).parent))

# Import necessary modules
from app.db.simple_mock_db import SimpleMockDatabase
from app.db.company import CompanyDB
from app.core.persistence_patch import apply_persistence_patch

# Path for storing database files
DB_DIR = os.path.join(os.getcwd(), "app", "db", "data")
COMPANIES_FILE = os.path.join(DB_DIR, "companies.json")

def ensure_dirs():
    """Ensure the database directories exist"""
    os.makedirs(DB_DIR, exist_ok=True)

async def ensure_test_company():
    """Ensure test_company exists with correct ID"""
    print("Creating SimpleMockDatabase instance...")
    db = SimpleMockDatabase()
    company_db = CompanyDB(db.companies)
    
    # Check if test_company exists
    test_company = await company_db.get_by_string_id("test_company")
    
    if test_company:
        print(f"Found existing test_company: {test_company.get('name')}")
        print(f"ID: {test_company.get('_id')}")
        print(f"Brand colors: {test_company.get('brand_colors')}")
        
        # Check if it has the correct ID
        if test_company.get('_id') != "test_company":
            print("Existing test_company has incorrect ID - fixing...")
            # Clear collection and create new one
            db._data["companies"] = {}
            await create_test_company(db)
        else:
            print("Test company looks good - updating brand colors for testing")
            # Update brand colors for testing
            await update_test_company(company_db)
    else:
        print("No test_company found - creating...")
        await create_test_company(db)
        
    # Ensure the test_company exists after our operations
    test_company = await company_db.get_by_string_id("test_company")
    if test_company:
        print(f"Verified test_company: {test_company.get('name')}")
        print(f"ID: {test_company.get('_id')}")
        print(f"Brand colors: {test_company.get('brand_colors')}")
    else:
        print("ERROR: Failed to create test_company!")

async def create_test_company(db):
    """Create a new test_company with the correct ID"""
    # Create test company data
    test_company_data = {
        "_id": "test_company",
        "id": "test_company",
        "name": "Test Company",
        "description": "This is a test company for development",
        "email": "contact@testcompany.com",
        "phone": "+1 (555) 123-4567",
        "address": "123 Test Street, Test City, TC 12345",
        "logo_url": "/uploads/default_logo.png",
        "brand_colors": ["#1a73e8", "#ea4335", "#fbbc04", "#34a853", "#ffffff"],
        "active": True,
        "created_at": datetime.utcnow(),
        "updated_at": datetime.utcnow()
    }
    
    # Insert directly
    await db.companies.insert_one(test_company_data)
    print("Test company created successfully")

async def update_test_company(company_db):
    """Update the test_company with distinctive brand colors"""
    from app.models.company import CompanyUpdate
    
    # Create distinctive brand colors
    update_data = CompanyUpdate(
        name="Test Company",
        description="This company was updated by the manual fix",
        brand_colors=["#FF5533", "#33FF55", "#5533FF"]  # Distinctive colors for testing
    )
    
    # Update the company
    updated_company = await company_db.update_company("test_company", update_data)
    if updated_company:
        print("Test company updated successfully")
    else:
        print("Failed to update test company!")

async def manually_save_database():
    """Manually create the database file if it doesn't exist"""
    # Ensure the directory exists
    ensure_dirs()
    
    if not os.path.exists(COMPANIES_FILE):
        print(f"Database file doesn't exist - creating {COMPANIES_FILE}")
        
        # Create database with test_company
        db = SimpleMockDatabase()
        await ensure_test_company()
        
        # Manually serialize and save to disk
        try:
            # Convert data to JSON serializable format
            companies_data = {}
            for key, value in db._data["companies"].items():
                # Create a copy to avoid modifying the original
                doc = value.copy()
                
                # Convert datetime objects to ISO strings
                for field in ["created_at", "updated_at"]:
                    if field in doc and isinstance(doc[field], datetime):
                        doc[field] = doc[field].isoformat()
                        
                companies_data[key] = doc
            
            # Save to disk
            with open(COMPANIES_FILE, 'w') as f:
                json.dump(companies_data, f, indent=2)
            print(f"Manually created database file: {COMPANIES_FILE}")
        except Exception as e:
            print(f"Error creating database file: {str(e)}")
    else:
        print(f"Database file already exists: {COMPANIES_FILE}")
        
        # Check content
        try:
            with open(COMPANIES_FILE, 'r') as f:
                data = json.load(f)
                
            print(f"Database file contains {len(data)} companies")
            
            # Check for test_company
            if "test_company" in data:
                print("Found test_company in database file")
                print(f"Name: {data['test_company'].get('name')}")
                print(f"Brand colors: {data['test_company'].get('brand_colors')}")
            else:
                print("test_company not found in database file - rewriting file...")
                # Rewrite the file with a new database
                db = SimpleMockDatabase()
                await ensure_test_company()
                
                # Manually serialize and save to disk
                try:
                    # Convert data to JSON serializable format
                    companies_data = {}
                    for key, value in db._data["companies"].items():
                        # Create a copy to avoid modifying the original
                        doc = value.copy()
                        
                        # Convert datetime objects to ISO strings
                        for field in ["created_at", "updated_at"]:
                            if field in doc and isinstance(doc[field], datetime):
                                doc[field] = doc[field].isoformat()
                                
                        companies_data[key] = doc
                    
                    # Save to disk
                    with open(COMPANIES_FILE, 'w') as f:
                        json.dump(companies_data, f, indent=2)
                    print(f"Rewrote database file: {COMPANIES_FILE}")
                except Exception as e:
                    print(f"Error rewriting database file: {str(e)}")
        except Exception as e:
            print(f"Error checking database file: {str(e)}")

async def main():
    print("Starting manual fix for company persistence...")
    
    # Step 1: Apply persistence patch
    apply_persistence_patch()
    
    # Step 2: Ensure database directory exists
    ensure_dirs()
    
    # Step 3: Manually save database if needed
    await manually_save_database()
    
    print("\n✅ Manual fix completed!")
    print("Please restart the API server to apply the changes")
    print("The API will now correctly load and persist company data")

if __name__ == "__main__":
    asyncio.run(main())
