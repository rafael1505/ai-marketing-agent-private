#!/usr/bin/env python3
"""
Fix company ID mismatch in the database file

This script ensures that the company ID in the database file
matches the expected ID (test_company) and is stored under
the correct key.
"""

import json
import os
import sys
import shutil
from datetime import datetime

DATABASE_PATH = "app/db/data/companies.json"
BACKUP_PATH = f"app/db/data/companies.json.backup.{datetime.now().strftime('%Y%m%d%H%M%S')}"
EXPECTED_ID = "test_company"

def fix_company_id():
    """Fix the company ID mismatch in the database file"""
    db_path = os.path.join(os.path.dirname(os.path.abspath(__file__)), DATABASE_PATH)
    
    if not os.path.exists(db_path):
        print(f"Database file does not exist at {db_path}")
        return False
    
    # Create a backup
    backup_path = os.path.join(os.path.dirname(os.path.abspath(__file__)), BACKUP_PATH)
    shutil.copy2(db_path, backup_path)
    print(f"Created backup at {backup_path}")
    
    try:
        # Read the current database
        with open(db_path, 'r') as f:
            db_data = json.load(f)
            
        # Find the test company
        found_id = None
        company_data = None
        
        for id_key, data in db_data.items():
            if data.get("_id") == EXPECTED_ID:
                found_id = id_key
                company_data = data
                break
        
        if not found_id:
            print(f"No company with _id={EXPECTED_ID} found in database")
            return False
            
        if found_id != EXPECTED_ID:
            print(f"Found company with _id={EXPECTED_ID} stored under key {found_id}")
            print("Fixing ID mismatch...")
            
            # Create a new database with the correct keys
            new_db = {}
            for id_key, data in db_data.items():
                if id_key == found_id:
                    # Store under the correct key
                    new_db[EXPECTED_ID] = data
                else:
                    # Keep other entries as is
                    new_db[id_key] = data
            
            # Write the corrected database back
            with open(db_path, 'w') as f:
                json.dump(new_db, f, indent=2)
                
            print("Database updated successfully")
            
            # Verify the fix
            with open(db_path, 'r') as f:
                updated_db = json.load(f)
                
            if EXPECTED_ID in updated_db:
                print(f"✅ Verification successful: Company now stored under key {EXPECTED_ID}")
                return True
            else:
                print(f"❌ Verification failed: Company not found under key {EXPECTED_ID}")
                return False
        else:
            print(f"✅ Company already stored under correct key {EXPECTED_ID}")
            return True
            
    except Exception as e:
        print(f"Error fixing company ID: {e}")
        return False
        
if __name__ == "__main__":
    success = fix_company_id()
    sys.exit(0 if success else 1)
