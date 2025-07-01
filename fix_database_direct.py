#!/usr/bin/env python3
"""
Direct database modification script to fix persistence issues with company data.
This script directly edits the mock database JSON file that stores the company data.
"""

import json
import os
import sys
import time

def fix_database():
    print("=== DIRECT DATABASE FIX ===\n")
    
    # Find the database file location
    db_file = os.path.join('app', 'db', 'mock_db.json')
    backup_file = os.path.join('app', 'db', 'mock_db.backup.json')
    
    if not os.path.exists(db_file):
        print(f"❌ Database file not found: {db_file}")
        return False
    
    # Create a backup of the current database
    print(f"Creating backup of database: {backup_file}")
    try:
        with open(db_file, 'r') as src, open(backup_file, 'w') as dst:
            dst.write(src.read())
    except Exception as e:
        print(f"❌ Failed to create backup: {e}")
        return False
    
    # Read the current database content
    try:
        with open(db_file, 'r') as f:
            db_content = json.load(f)
    except Exception as e:
        print(f"❌ Failed to read database: {e}")
        return False
    
    # Check if the database has the expected structure
    if 'companies' not in db_content:
        print(f"❌ Database missing 'companies' collection")
        return False
    
    companies = db_content['companies']
    if not isinstance(companies, list):
        print(f"❌ Companies collection is not a list: {type(companies)}")
        return False
    
    # Find active company
    active_company = None
    active_company_index = -1
    
    for i, company in enumerate(companies):
        if company.get('active', False) is True:
            active_company = company
            active_company_index = i
            break
    
    if not active_company:
        print("❌ No active company found in database")
        return False
    
    print(f"Found active company: {active_company.get('name')}")
    print(f"ID: {active_company.get('id')}, _id: {active_company.get('_id')}")
    
    # Fix the company data
    fixed_company = fix_company_structure(active_company)
    
    # Replace in the database
    db_content['companies'][active_company_index] = fixed_company
    
    # Write updated database back to file
    try:
        with open(db_file, 'w') as f:
            json.dump(db_content, f, indent=2)
        print("✅ Updated database file successfully")
    except Exception as e:
        print(f"❌ Failed to write database: {e}")
        return False
    
    # Print verification
    print("\nVerifying database changes...")
    time.sleep(1)  # Wait a moment for file to sync
    
    try:
        with open(db_file, 'r') as f:
            verify_db = json.load(f)
        
        if 'companies' not in verify_db:
            print("❌ Verification failed: 'companies' collection missing")
            return False
            
        verify_company = None
        for company in verify_db['companies']:
            if company.get('active', False) is True:
                verify_company = company
                break
        
        if not verify_company:
            print("❌ Verification failed: no active company found")
            return False
        
        print(f"Verified company: {verify_company.get('name')}")
        print(f"Brand colors: {verify_company.get('brand_colors')}")
        
        # Test the colors and logo
        has_valid_colors = isinstance(verify_company.get('brand_colors'), list) and len(verify_company.get('brand_colors', [])) > 0
        has_valid_logo = verify_company.get('logo_url') and not verify_company.get('logo_url', '').startswith('blob:')
        
        print(f"Has valid brand colors: {'✓' if has_valid_colors else '✗'}")
        print(f"Has valid logo URL: {'✓' if has_valid_logo else '✗'}")
        
        return has_valid_colors and has_valid_logo
    except Exception as e:
        print(f"❌ Verification failed: {e}")
        return False

def fix_company_structure(company):
    """Apply all necessary fixes to the company object"""
    # Create a copy to avoid modifying the original
    fixed = dict(company)
    
    # Fix brand_colors
    if 'brand_colors' not in fixed or not fixed['brand_colors']:
        print("Setting default brand colors")
        fixed['brand_colors'] = ["#FF0000", "#00FF00", "#0000FF"]  # Red, Green, Blue
    elif not isinstance(fixed['brand_colors'], list):
        print(f"Converting brand_colors to list: {fixed['brand_colors']}")
        try:
            fixed['brand_colors'] = list(fixed['brand_colors'])
        except:
            fixed['brand_colors'] = ["#3B82F6"]  # Default blue
    
    # Ensure not empty, no blob URLs, and all items are strings
    brand_colors = []
    for color in fixed['brand_colors']:
        if color and isinstance(color, str) and not color.startswith('blob:'):
            # Check if it might be a JSON string
            if color.startswith('[') and color.endswith(']'):
                try:
                    parsed = json.loads(color)
                    if isinstance(parsed, list):
                        brand_colors.extend([c for c in parsed if c and isinstance(c, str)])
                    else:
                        brand_colors.append(str(parsed))
                except:
                    brand_colors.append(color)
            else:
                brand_colors.append(color)
    
    # If after all processing we have no colors, add a default
    if not brand_colors:
        brand_colors = ["#3B82F6"]  # Default blue
    
    fixed['brand_colors'] = brand_colors
    print(f"Final brand_colors: {fixed['brand_colors']}")
    
    # Fix logo_url
    if 'logo_url' not in fixed or not fixed['logo_url']:
        print("Setting default logo URL")
        fixed['logo_url'] = "/uploads/default_logo.png"
    elif isinstance(fixed['logo_url'], str) and fixed['logo_url'].startswith('blob:'):
        print(f"Removing blob URL: {fixed['logo_url']}")
        fixed['logo_url'] = "/uploads/default_logo.png"
    
    print(f"Final logo_url: {fixed['logo_url']}")
    
    # Ensure required fields exist
    required_fields = {
        'name': 'Test Company',
        'description': 'This is a test company for development',
        'active': True
    }
    
    for field, default in required_fields.items():
        if field not in fixed or fixed[field] is None:
            print(f"Setting default {field}: {default}")
            fixed[field] = default
    
    # Ensure ID fields are consistent
    company_id = fixed.get('id') or fixed.get('_id') or 'test_company'
    fixed['_id'] = company_id
    fixed['id'] = company_id
    
    return fixed

if __name__ == "__main__":
    if fix_database():
        print("\n✅ Database fixed successfully!")
        sys.exit(0)
    else:
        print("\n❌ Failed to fix database!")
        sys.exit(1)
