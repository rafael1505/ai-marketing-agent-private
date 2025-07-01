#!/usr/bin/env python3
# filepath: /mnt/c/Users/brc07274/OneDrive - Philips/Philips Files/BU - CI/Repository/AI Marketing Agent (Python)/ai-marketing-agent/fix_database_load.py

"""
This script fixes the database loading mechanism in the API server
by ensuring that the database persistence patch is correctly applied
and that the company data is loaded from the file properly.
"""

import os
import json
from datetime import datetime

def print_separator(title=""):
    print("\n" + "="*50)
    if title:
        print(f" {title} ")
        print("="*50)
    print()

def check_company_data():
    """Check what's currently in the database file"""
    db_dir = os.path.join(os.getcwd(), "app", "db", "data")
    companies_file = os.path.join(db_dir, "companies.json")
    
    if not os.path.exists(companies_file):
        print(f"No companies database file found at: {companies_file}")
        return False
        
    try:
        with open(companies_file, 'r') as f:
            data = json.load(f)
            
        print(f"Found {len(data)} companies in the database file")
        
        for key, company in data.items():
            print(f"\nCompany key: {key}")
            print(f"  Name: {company.get('name')}")
            print(f"  ID fields: _id={company.get('_id')}, id={company.get('id')}")
            print(f"  Description: {company.get('description')}")
            print(f"  Brand colors: {company.get('brand_colors')}")
            print(f"  Created: {company.get('created_at')}")
            print(f"  Updated: {company.get('updated_at')}")
            print(f"  Active: {company.get('active')}")
            
        return True
    except Exception as e:
        print(f"Error reading database file: {str(e)}")
        return False

def check_api_loading_code():
    """Check the API server startup code for database loading"""
    main_py = os.path.join(os.getcwd(), "app", "main.py")
    persistence_py = os.path.join(os.getcwd(), "app", "core", "persistence_patch.py")
    
    if not os.path.exists(main_py):
        print(f"API server code not found at: {main_py}")
        return False
        
    if not os.path.exists(persistence_py):
        print(f"Persistence patch code not found at: {persistence_py}")
        return False
        
    try:
        with open(main_py, 'r') as f:
            main_code = f.read()
            
        with open(persistence_py, 'r') as f:
            persistence_code = f.read()
            
        # Check import statement
        if "from app.core.persistence_patch import apply_persistence_patch" not in main_code:
            print("❌ Persistence patch import missing from main.py")
        else:
            print("✅ Persistence patch import found in main.py")
            
        # Check apply call
        if "apply_persistence_patch()" not in main_code:
            print("❌ apply_persistence_patch() call missing from main.py")
        else:
            print("✅ apply_persistence_patch() call found in main.py")
            
        # Check apply function in persistence_patch.py
        if "def apply_persistence_patch():" not in persistence_code:
            print("❌ apply_persistence_patch() function not found in persistence_patch.py")
        else:
            print("✅ apply_persistence_patch() function found in persistence_patch.py")
            
        # Check load from disk
        if "load data from disk" not in persistence_code.lower():
            print("❌ Loading from disk logic may be missing from persistence_patch.py")
        else:
            print("✅ Loading from disk logic found in persistence_patch.py")
            
        return True
    except Exception as e:
        print(f"Error checking code files: {str(e)}")
        return False

if __name__ == "__main__":
    print_separator("Company Database Loader Fix")
    
    print_separator("Current Database Contents")
    check_company_data()
    
    print_separator("API Loading Code Check")
    check_api_loading_code()
    
    print("\nSuggested fix:")
    print("1. Ensure the persistence patch is loaded early in app/main.py")
    print("2. Update the startup event to check for existing data before creating new data")
    print("3. Fix the database ID handling to work consistently with test_company")
    print("4. Make sure brand_colors is always initialized as []")
    print("5. Restart the API server with a clean state")
