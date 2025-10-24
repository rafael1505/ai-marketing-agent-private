#!/usr/bin/env python3
"""
Fix company data persistence by directly modifying the companies.json file.
"""

import os
import json
import shutil
from datetime import datetime

# Path for storing database files
DB_DIR = os.path.join(os.getcwd(), "app", "db", "data")
COMPANIES_FILE = os.path.join(DB_DIR, "companies.json")
BACKUP_DIR = os.path.join(DB_DIR, "backups")

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

def fix_company_data():
    print("=== COMPANY DATA PERSISTENCE FIX ===\n")
    
    # Ensure directories exist
    ensure_dirs()
    
    # Check if companies file exists
    if not os.path.exists(COMPANIES_FILE):
        print("Companies file does not exist, will be created with default data")
        companies_data = {}
    else:
        # Create backup
        backup_db_file(COMPANIES_FILE)
        
        # Load current data
        try:
            with open(COMPANIES_FILE, 'r') as f:
                companies_data = json.load(f)
                print(f"Loaded company data with {len(companies_data)} entries")
        except Exception as e:
            print(f"Error loading companies file: {e}")
            print("Creating new data")
            companies_data = {}
    
    # Find active company
    active_company_id = None
    active_company = None
    
    for company_id, company in companies_data.items():
        if company.get('active', False):
            active_company_id = company_id
            active_company = company
            break
    
    if not active_company:
        print("No active company found, creating default test company")
        active_company_id = "test_company"
        active_company = {
            "id": "test_company",
            "_id": "test_company",
            "name": "Test Company",
            "description": "This is a test company for development",
            "email": "contact@testcompany.com", 
            "phone": "+1 (555) 123-4567",
            "address": "123 Test Street, Test City, TC 12345",
            "logo_url": "/uploads/default_logo.png",
            "brand_colors": ["#3B82F6", "#A855F7"],
            "active": True,
            "created_at": datetime.utcnow().isoformat(),
            "updated_at": datetime.utcnow().isoformat()
        }
        companies_data[active_company_id] = active_company
        print("Created new test company")
    else:
        print(f"Found active company: {active_company.get('name')}")
        print(f"ID: {active_company.get('id')}, _id: {active_company.get('_id')}")
    
    # Fix brand colors
    print("\nFixing brand colors...")
    
    brand_colors = active_company.get('brand_colors')
    
    if not brand_colors:
        print("Setting default brand colors")
        brand_colors = ["#FF0000", "#00FF00", "#0000FF"]  # Red, Green, Blue
    elif not isinstance(brand_colors, list):
        print(f"Converting brand_colors to list: {brand_colors}")
        try:
            brand_colors = list(brand_colors)
        except:
            brand_colors = ["#3B82F6"]  # Default blue
    
    # Process all colors to handle JSON strings
    processed_colors = []
    for color in brand_colors:
        if color and isinstance(color, str):
            # Check if this might be a JSON string that needs to be parsed
            if color.startswith('[') and color.endswith(']'):
                try:
                    # Try to parse JSON array
                    parsed_colors = json.loads(color)
                    if isinstance(parsed_colors, list):
                        # Add all colors from the parsed array
                        for c in parsed_colors:
                            if c and isinstance(c, str):
                                processed_colors.append(c)
                        continue  # Skip adding the original JSON string
                except json.JSONDecodeError:
                    # Not valid JSON, use as is
                    processed_colors.append(color)
            else:
                processed_colors.append(color)
                
    # Use processed colors or default
    if processed_colors:
        brand_colors = processed_colors
    else:
        brand_colors = ["#3B82F6"]  # Default blue
        
    print(f"Updated brand_colors: {brand_colors}")
    active_company['brand_colors'] = brand_colors
    
    # Fix logo URL
    print("\nFixing logo URL...")
    
    logo_url = active_company.get('logo_url')
    
    if not logo_url:
        print("Setting default logo URL")
        logo_url = "/uploads/default_logo.png"
    elif logo_url.startswith('blob:'):
        print("Removing blob URL")
        logo_url = "/uploads/default_logo.png"
        
    print(f"Updated logo_url: {logo_url}")
    active_company['logo_url'] = logo_url
    
    # Fix IDs
    company_id = active_company.get('id') or active_company.get('_id') or 'test_company'
    active_company['id'] = company_id
    active_company['_id'] = company_id
    print(f"\nConsistent company ID set to: {company_id}")
    
    # Ensure active company is in the dictionary with the right key
    companies_data[company_id] = active_company
    
    # Update timestamps
    active_company['updated_at'] = datetime.utcnow().isoformat()
    
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
        
        if company_id not in verify_data:
            print(f"❌ Company {company_id} not found in saved data!")
            return False
            
        saved_company = verify_data[company_id]
        
        # Check brand colors
        saved_colors = saved_company.get('brand_colors', [])
        if not isinstance(saved_colors, list) or len(saved_colors) == 0:
            print("❌ Brand colors verification failed!")
            return False
            
        # Check logo URL
        saved_logo = saved_company.get('logo_url', '')
        if not saved_logo or saved_logo.startswith('blob:'):
            print("❌ Logo URL verification failed!")
            return False
            
        print(f"✓ Company name: {saved_company.get('name')}")
        print(f"✓ Brand colors: {saved_colors}")
        print(f"✓ Logo URL: {saved_logo}")
        print("\n✅ ALL CHANGES VERIFIED!")
        return True
        
    except Exception as e:
        print(f"\n❌ Error verifying company data: {e}")
        return False

if __name__ == "__main__":
    fix_company_data()
