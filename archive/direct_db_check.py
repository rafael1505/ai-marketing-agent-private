#!/usr/bin/env python3
# filepath: /mnt/c/Users/brc07274/OneDrive - Philips/Philips Files/BU - CI/Repository/AI Marketing Agent (Python)/ai-marketing-agent/direct_db_check.py
import json
import os

"""
Direct check of the database file without using the app's database classes
This will help us understand what's stored in the database directly
"""

def check_db_file():
    db_dir = os.path.join(os.getcwd(), "app", "db", "data")
    company_file = os.path.join(db_dir, "companies.json")
    
    print(f"Checking if database file exists at: {company_file}")
    
    if not os.path.exists(company_file):
        print(f"Database file not found!")
        return
    
    print(f"Database file found. Reading content...")
    
    try:
        with open(company_file, 'r') as f:
            content = f.read()
            data = json.loads(content)
            
        print(f"\nDatabase content:")
        print(json.dumps(data, indent=2))
        
        # Look for test_company
        test_company = None
        for item in data:
            if item.get('_id') == 'test_company' or item.get('id') == 'test_company':
                test_company = item
                break
                
        if test_company:
            print(f"\nFound test_company:")
            print(json.dumps(test_company, indent=2))
        else:
            print(f"\nNo test_company found in database")
        
        # Look for active company
        active_company = None
        for item in data:
            if item.get('active') == True:
                active_company = item
                break
                
        if active_company:
            print(f"\nFound active company:")
            print(json.dumps(active_company, indent=2))
        else:
            print(f"\nNo active company found in database")
            
    except Exception as e:
        print(f"Error reading database file: {str(e)}")

if __name__ == "__main__":
    check_db_file()
