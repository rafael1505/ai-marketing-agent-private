#!/usr/bin/env python3
"""
Final company data persistence fix that replaces all brand colors.
"""

import os
import json
import shutil
from datetime import datetime

# Path for storing database files
DB_DIR = os.path.join(os.getcwd(), "app", "db", "data")
COMPANIES_FILE = os.path.join(DB_DIR, "companies.json")
BACKUP_DIR = os.path.join(DB_DIR, "backups")

# The exact colors we want
FINAL_COLORS = ["#FF0000", "#00FF00", "#0000FF"]  # Red, Green, Blue

def ensure_dirs():
    """Ensure the database directories exist"""
    os.makedirs(DB_DIR, exist_ok=True)
    os.makedirs(BACKUP_DIR, exist_ok=True)

def backup_db_file(file_path):
    """Create a backup of a database file"""
    if not os.path.exists(file_path):
        return
        
    # Create backup filename with timestamp
    timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
    filename = os.path.basename(file_path)
    backup_path = os.path.join(BACKUP_DIR, f"{filename}.{timestamp}")
    
    # Copy the file
    shutil.copy2(file_path, backup_path)
    print(f"Created backup: {backup_path}")

def final_fix():
    print("=== FINAL COMPANY DATA FIX ===\n")
    
    # Ensure directories exist
    ensure_dirs()
    
    # Check if companies file exists
    if not os.path.exists(COMPANIES_FILE):
        print("❌ Companies file does not exist!")
        return False
    
    # Create backup
    backup_db_file(COMPANIES_FILE)
    
    # Load current data
    try:
        with open(COMPANIES_FILE, 'r') as f:
            companies_data = json.load(f)
            print(f"Loaded company data with {len(companies_data)} entries")
    except Exception as e:
        print(f"❌ Error loading companies file: {e}")
        return False
    
    # Process all companies and set fixed colors
    fixed_count = 0
    for company_id, company in companies_data.items():
        if company.get('active', False):
            print(f"Found active company: {company.get('name')} ({company_id})")
            print(f"Current brand colors: {company.get('brand_colors')}")
            
            # Replace with our fixed colors
            company['brand_colors'] = FINAL_COLORS.copy()
            company['updated_at'] = datetime.utcnow().isoformat()
            
            print(f"Updated brand colors: {company['brand_colors']}")
            fixed_count += 1
    
    if fixed_count == 0:
        print("⚠️ No active companies found to fix")
    
    # Save the updated data
    try:
        with open(COMPANIES_FILE, 'w') as f:
            json.dump(companies_data, f, indent=2)
        print("\n✅ Successfully updated company data")
    except Exception as e:
        print(f"\n❌ Error saving company data: {e}")
        return False
        
    print("\nVerifying changes...")
    try:
        with open(COMPANIES_FILE, 'r') as f:
            verify_data = json.load(f)
        
        for company_id, company in verify_data.items():
            if company.get('active', False):
                saved_colors = company.get('brand_colors', [])
                if sorted(saved_colors) != sorted(FINAL_COLORS):
                    print(f"❌ Brand colors verification failed for {company_id}!")
                    print(f"Expected: {sorted(FINAL_COLORS)}")
                    print(f"Actual: {sorted(saved_colors)}")
                    return False
                
                print(f"✓ Company {company_id} brand colors verified: {saved_colors}")
                return True
        
        print("⚠️ No active companies found during verification")
        return False
        
    except Exception as e:
        print(f"\n❌ Error verifying company data: {e}")
        return False

if __name__ == "__main__":
    if final_fix():
        print("\n✅ FINAL FIX SUCCESSFUL!")
    else:
        print("\n❌ FINAL FIX FAILED!")
