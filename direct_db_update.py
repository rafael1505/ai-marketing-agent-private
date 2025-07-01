#!/usr/bin/env python3
"""
Direct Database Test Script

This script bypasses the API and works directly with the database file to:
1. Read the current company data
2. Update the company name and brand colors
3. Verify the changes were persisted
"""

import os
import json
import sys
import datetime
from pathlib import Path

# Constants
DATABASE_PATH = "app/db/data/companies.json"
TEST_COMPANY_ID = "test_company"
TEST_COMPANY_NAME = f"DB Direct Test Company {datetime.datetime.now().strftime('%H:%M:%S')}"
TEST_BRAND_COLORS = ["#8BC34A", "#FF9800", "#03A9F4", "#F44336", "#9C27B0"]

def read_database():
    """Read the database file"""
    print(f"Reading database from {DATABASE_PATH}")
    
    if not os.path.exists(DATABASE_PATH):
        print(f"❌ Database file does not exist at {DATABASE_PATH}")
        return None
        
    try:
        with open(DATABASE_PATH, 'r') as f:
            data = json.load(f)
        print(f"✅ Read database with {len(data)} entries")
        return data
    except Exception as e:
        print(f"❌ Error reading database: {e}")
        return None

def save_database(data):
    """Save the database file"""
    print(f"Saving database to {DATABASE_PATH}")
    
    try:
        # Create backup first
        if os.path.exists(DATABASE_PATH):
            backup_path = f"{DATABASE_PATH}.bak"
            with open(backup_path, 'w') as f:
                with open(DATABASE_PATH, 'r') as src:
                    f.write(src.read())
            print(f"✅ Created backup at {backup_path}")
            
        # Save new data
        with open(DATABASE_PATH, 'w') as f:
            json.dump(data, f, indent=2)
        print(f"✅ Saved database to {DATABASE_PATH}")
        return True
    except Exception as e:
        print(f"❌ Error saving database: {e}")
        return False

def update_company(db_data):
    """Update the company in the database"""
    if TEST_COMPANY_ID not in db_data:
        print(f"❌ Company with ID '{TEST_COMPANY_ID}' not found in database")
        return False
        
    company = db_data[TEST_COMPANY_ID]
    
    print("Current company data:")
    print(f"Name: {company.get('name', 'None')}")
    print(f"Brand colors: {company.get('brand_colors', 'None')}")
    
    # Update company
    company["name"] = TEST_COMPANY_NAME
    company["brand_colors"] = TEST_BRAND_COLORS
    company["updated_at"] = datetime.datetime.now().isoformat()
    
    # Save back to database
    db_data[TEST_COMPANY_ID] = company
    
    return True

def verify_update():
    """Verify the update was persisted"""
    db_data = read_database()
    if not db_data:
        return False
        
    if TEST_COMPANY_ID not in db_data:
        print(f"❌ Company with ID '{TEST_COMPANY_ID}' not found in database")
        return False
        
    company = db_data[TEST_COMPANY_ID]
    
    print("\nVerifying update:")
    
    # Check name
    if company.get("name") == TEST_COMPANY_NAME:
        print(f"✅ Name updated correctly: {company.get('name')}")
        name_ok = True
    else:
        print(f"❌ Name not updated correctly: {company.get('name')} != {TEST_COMPANY_NAME}")
        name_ok = False
        
    # Check brand colors
    if company.get("brand_colors") == TEST_BRAND_COLORS:
        print(f"✅ Brand colors updated correctly: {company.get('brand_colors')}")
        colors_ok = True
    else:
        print(f"❌ Brand colors not updated correctly: {company.get('brand_colors')} != {TEST_BRAND_COLORS}")
        colors_ok = False
        
    return name_ok and colors_ok

def main():
    """Main execution function"""
    print("\n" + "="*50)
    print("  DIRECT DATABASE UPDATE TEST")
    print("="*50 + "\n")
    
    # Read database
    db_data = read_database()
    if not db_data:
        print("❌ Could not read database")
        return False
        
    # Update company
    print("\nUpdating company...")
    if not update_company(db_data):
        print("❌ Failed to update company")
        return False
        
    # Save database
    if not save_database(db_data):
        print("❌ Failed to save database")
        return False
        
    # Verify update
    print("\nVerifying update...")
    success = verify_update()
    
    print("\n" + "="*50)
    if success:
        print("✅✅✅ DIRECT DATABASE UPDATE SUCCESSFUL")
        print("Company data has been updated and persisted")
    else:
        print("❌❌❌ DIRECT DATABASE UPDATE FAILED")
        print("Update was not properly persisted")
    print("="*50)
    
    return success

if __name__ == "__main__":
    success = main()
    sys.exit(0 if success else 1)
