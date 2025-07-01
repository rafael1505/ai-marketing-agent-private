#!/usr/bin/env python3
"""
Fix script for the test_company ID issue in the mock database.
This script will ensure the test_company exists and is properly configured.
"""

from app.db.simple_mock_db import SimpleMockDatabase
from datetime import datetime
import json

def fix_test_company():
    """Fix the test_company ID in the mock database"""
    print("Starting test_company fix...")
    
    # Create a new instance of the mock database
    db = SimpleMockDatabase()
    companies_collection = db.companies
    
    # Check what companies exist
    print("\nChecking existing companies in mock database...")
    
    # Get a list of all companies (have to get one by one in the simple mock)
    companies = []
    for id_val in db._data["companies"]:
        companies.append({**db._data["companies"][id_val], "_id": id_val})
    
    print(f"Found {len(companies)} companies:")
    for c in companies:
        print(f"- ID: {c.get('_id')}, Name: {c.get('name')}, Active: {c.get('active', False)}")
    
    # Check if test_company exists
    test_company_exists = "test_company" in db._data["companies"]
    print(f"\ntest_company exists: {test_company_exists}")
    
    # Find the active company
    active_company = None
    for id_val, company in db._data["companies"].items():
        if company.get("active", False):
            active_company = {**company, "_id": id_val}
            break
    
    print(f"Active company: {active_company['name'] if active_company else 'None'}")
    
    # Create test_company if it doesn't exist
    if not test_company_exists:
        print("\nCreating test_company...")
        
        # If there's an active company, copy its data
        if active_company:
            print(f"Using data from active company: {active_company['name']}")
            new_company = active_company.copy()
            
            # Remove _id if it exists (we'll set it to test_company)
            if "_id" in new_company:
                del new_company["_id"]
        else:
            # Create a default company
            print("No active company found, creating default test_company")
            new_company = {
                "name": "Test Company",
                "description": "Test company for development",
                "email": "contact@testcompany.com",
                "phone": "+1 (555) 123-4567",
                "address": "123 Test Street, Test City, TC 12345",
                "logo_url": "/uploads/default_logo.png",
                "brand_colors": ["#FF0000", "#00FF00", "#0000FF"],
                "active": True,
                "created_at": datetime.utcnow().isoformat(),
                "updated_at": datetime.utcnow().isoformat()
            }
        
        # Set company to active
        new_company["active"] = True
        
        # Make sure brand_colors is a list
        if "brand_colors" not in new_company or new_company["brand_colors"] is None:
            new_company["brand_colors"] = []
        
        # Insert the company with _id = "test_company"
        db._data["companies"]["test_company"] = new_company
        print("test_company created successfully")
    else:
        # Update the existing test_company
        print("\nUpdating existing test_company...")
        
        # Get the existing test_company
        test_company = db._data["companies"]["test_company"]
        
        # Set it to active
        test_company["active"] = True
        
        # Make sure brand_colors is a list
        if "brand_colors" not in test_company or test_company["brand_colors"] is None:
            test_company["brand_colors"] = []
        
        # Update timestamp
        test_company["updated_at"] = datetime.utcnow().isoformat()
        
        print("test_company updated successfully")
    
    # Make sure all companies with active=True also have an _id=test_company
    for id_val, company in list(db._data["companies"].items()):
        if company.get("active", False) and id_val != "test_company":
            print(f"\nFound active company with ID {id_val}, migrating data to test_company")
            
            # Copy the data from this company to test_company if test_company exists
            if "test_company" in db._data["companies"]:
                # Merge data, keeping test_company's _id and id
                db._data["companies"]["test_company"].update({
                    k: v for k, v in company.items()
                    if k not in ["_id", "id"]
                })
                print("Data merged into test_company")
            
            # Set this company to inactive
            db._data["companies"][id_val]["active"] = False
            print(f"Set company {id_val} to inactive")
    
    # Verify the fix worked
    print("\nVerifying fix...")
    test_company = db._data["companies"].get("test_company")
    if test_company:
        print("✅ test_company exists")
        print(f"Name: {test_company['name']}")
        print(f"Active: {test_company.get('active', False)}")
        print(f"Brand colors: {test_company.get('brand_colors', [])}")
        
        # Check if it's active
        if test_company.get("active", False):
            print("✅ test_company is active")
        else:
            print("❌ test_company is not active")
            test_company["active"] = True
            print("Fixed: Set test_company to active")
    else:
        print("❌ test_company still doesn't exist")
    
    # Print all companies again to verify
    print("\nFinal company list:")
    for id_val, company in db._data["companies"].items():
        print(f"- ID: {id_val}, Name: {company.get('name')}, "
              f"Active: {company.get('active', False)}, "
              f"Brand colors: {company.get('brand_colors', [])}")
    
    # Save the changes back to the mock database data store if applicable
    print("\nDone! Changes have been applied to the in-memory database.")
    print("To persist these changes, restart the API server.")

if __name__ == "__main__":
    fix_test_company()
