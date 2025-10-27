#!/usr/bin/env python3
# filepath: /mnt/c/Users/brc07274/OneDrive - Philips/Philips Files/BU - CI/Repository/AI Marketing Agent (Python)/ai-marketing-agent/direct_company_update.py

"""
This script directly updates the company data in the saved database file.
It is used to debug and fix persistence issues with the company data.
"""

import os
import json
from datetime import datetime
import sys

# Path for storing database files
DB_DIR = os.path.join(os.getcwd(), "app", "db", "data")
COMPANIES_FILE = os.path.join(DB_DIR, "companies.json")
BACKUP_DIR = os.path.join(DB_DIR, "backups")

def ensure_dirs():
    """Ensure the database directories exist"""
    os.makedirs(DB_DIR, exist_ok=True)
    os.makedirs(BACKUP_DIR, exist_ok=True)

def backup_file(file_path):
    """Create a backup of a file"""
    if not os.path.exists(file_path):
        return None
        
    # Create backup filename with timestamp
    timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
    filename = os.path.basename(file_path)
    backup_path = os.path.join(BACKUP_DIR, f"{filename}.{timestamp}")
    
    # Copy the content
    with open(file_path, 'r') as src, open(backup_path, 'w') as dest:
        dest.write(src.read())
        
    print(f"Created backup: {backup_path}")
    return backup_path

def load_companies():
    """Load company data from the file"""
    ensure_dirs()
    if not os.path.exists(COMPANIES_FILE):
        return {}
        
    try:
        with open(COMPANIES_FILE, 'r') as f:
            return json.load(f)
    except Exception as e:
        print(f"Error loading companies: {str(e)}")
        return {}

def save_companies(data):
    """Save company data to the file"""
    ensure_dirs()
    backup_file(COMPANIES_FILE)
    
    try:
        with open(COMPANIES_FILE, 'w') as f:
            json.dump(data, f, indent=2)
        print(f"Saved company data to {COMPANIES_FILE}")
        return True
    except Exception as e:
        print(f"Error saving companies: {str(e)}")
        return False

def update_company(company_id, updates):
    """Update a company in the data file"""
    companies = load_companies()
    
    if not companies:
        print("No companies found in database")
        return False
        
    # Find company with either _id or id matching
    updated = False
    for key, company in companies.items():
        if (key == company_id or 
            company.get("id") == company_id or 
            company.get("_id") == company_id):
                
            # Update the company
            company.update(updates)
            company["updated_at"] = datetime.now().isoformat()
            updated = True
            print(f"Updated company {key}: {company}")
            break
    
    if not updated:
        # Try to find the active company
        for key, company in companies.items():
            if company.get("active") == True:
                # Update the company
                company.update(updates)
                company["updated_at"] = datetime.now().isoformat()
                updated = True
                print(f"Updated active company {key}: {company}")
                break
    
    if updated:
        return save_companies(companies)
    else:
        print(f"Company {company_id} not found")
        return False

def print_all_companies():
    """Print all companies in the database"""
    companies = load_companies()
    if not companies:
        print("No companies found in database")
        return
        
    print("\nAll companies in database:")
    for key, company in companies.items():
        print(f"Company ID: {key}")
        print(f"  Name: {company.get('name')}")
        print(f"  Description: {company.get('description')}")
        print(f"  Brand Colors: {company.get('brand_colors')}")
        print(f"  Is Active: {company.get('active')}")
        print(f"  Created: {company.get('created_at')}")
        print(f"  Updated: {company.get('updated_at')}")
        print()

if __name__ == "__main__":
    print("Direct Company Database Update Tool")
    print("==================================")
    print_all_companies()
    
    # Update the company with test data
    update_data = {
        "name": "Test Company",
        "description": "Updated with direct tool",
        "brand_colors": ["#FF0000", "#00FF00", "#0000FF", "#FFFF00"]
    }
    
    update_company("test_company", update_data)
    print("\nAfter update:")
    print_all_companies()
