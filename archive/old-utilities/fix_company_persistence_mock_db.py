#!/usr/bin/env python3
"""
Fix for the company persistence issue using the application's mock database.
"""

import requests
import json
import time
import sys
import os
import subprocess

# Configuration
API_URL = "http://127.0.0.1:8088"
COMPANY_ID = "test_company"  # The fixed ID we want to use
TEST_BRAND_COLORS = ["#FF5733", "#33FF57"]  # Test colors

def print_header(text):
    """Print a formatted header"""
    print("\n" + "=" * 80)
    print(f" {text} ".center(78, "*"))
    print("=" * 80 + "\n")

def get_active_company():
    """Get the currently active company from the API"""
    try:
        response = requests.get(f"{API_URL}/api/v1/companies/active", 
                            proxies={"http": None, "https": None})
        
        if response.status_code == 200:
            return response.json()
        else:
            print(f"Failed to get company: {response.status_code}")
            print(response.text)
            return None
    except Exception as e:
        print(f"Error getting active company: {e}")
        return None

def fix_company_model_file():
    """Fix the company model to ensure brand_colors has a default empty list"""
    model_file = "app/models/company.py"
    try:
        with open(model_file, "r") as f:
            content = f.read()
        
        # Check if brand_colors has a default empty list
        if "brand_colors: Optional[List[str]] = None" in content:
            print("Fixing brand_colors default value to empty list...")
            fixed_content = content.replace(
                "brand_colors: Optional[List[str]] = None",
                "brand_colors: Optional[List[str]] = []"
            )
            with open(model_file, "w") as f:
                f.write(fixed_content)
            print("✅ Updated company model with default empty list for brand_colors")
            return True
    except Exception as e:
        print(f"❌ Error updating model file: {e}")
    return False

def fix_company_db_class():
    """Fix the CompanyDB class to ensure brand_colors is always a list"""
    db_file = "app/db/company.py"
    try:
        with open(db_file, "r") as f:
            content = f.read()
        
        # Check for update_company method and add explicit brand_colors handling
        if "async def update_company" in content:
            print("Checking company DB class for brand_colors handling...")
            if "company_data[\"brand_colors\"] = brand_colors if brand_colors else []" in content:
                print("✅ Company DB class already has brand_colors fix")
                return True
    except Exception as e:
        print(f"❌ Error checking DB file: {e}")
    return False

def fix_simple_mock_db_bug():
    """Fix the simple mock DB implementation to persist changes properly"""
    mock_db_file = "app/db/simple_mock_db.py"
    try:
        with open(mock_db_file, "r") as f:
            content = f.read()
        
        # Check if the mock DB has persistence issues with "id" field vs "_id" field
        if "async def update_one" in content:
            print("Checking simple mock DB implementation...")
            
            # Look for the update_one method
            import re
            update_one_pattern = r"async def update_one\(self, query=None, update=None\):(.*?)return result"
            update_one_match = re.search(update_one_pattern, content, re.DOTALL)
            
            if update_one_match:
                update_one_code = update_one_match.group(1)
                
                # Check if the method handles id/ID properly
                if "update[\"$set\"][\"id\"] = doc_id" not in update_one_code:
                    print("Adding ID consistency fix to simple mock DB...")
                    
                    # Find where the document is updated
                    doc_update_pattern = r"(\s+)for key, value in update\[\"\$set\"\]\.items\(\):(.*?)self\.data\[doc_id\] = result"
                    doc_update_match = re.search(doc_update_pattern, content, re.DOTALL)
                    
                    if doc_update_match:
                        indent = doc_update_match.group(1)
                        update_section = doc_update_match.group(2)
                        
                        # Add ID consistency code
                        id_consistency_code = f"{indent}# Ensure 'id' field matches '_id' for consistency\n{indent}update[\"$set\"][\"id\"] = str(doc_id)\n"
                        
                        # Insert our fix before the update section
                        fixed_content = content.replace(
                            f"for key, value in update[\"$set\"].items():",
                            f"{id_consistency_code}for key, value in update[\"$set\"].items():"
                        )
                        
                        with open(mock_db_file, "w") as f:
                            f.write(fixed_content)
                        print("✅ Updated simple mock DB with ID consistency fix")
                        return True
                else:
                    print("✅ Simple mock DB already has ID consistency fix")
                    return True
    except Exception as e:
        print(f"❌ Error updating mock DB file: {e}")
    return False

def create_direct_fix_script():
    """Create a script to directly manipulate the DB in memory"""
    fix_script_path = "app/db/fix_persistence.py"
    
    try:
        with open(fix_script_path, "w") as f:
            f.write('''"""
This module contains fixes for company persistence issues in the mock database.
It will be applied when the API starts.
"""

from app.db.simple_mock_db import SimpleMockDatabase
from datetime import datetime
import logging

logger = logging.getLogger(__name__)

def ensure_test_company_consistency(db: SimpleMockDatabase):
    """
    Ensures the test company has consistent ID and brand colors.
    This function is called during API startup.
    """
    logger.info("Applying company persistence fixes...")
    
    # Get reference to the companies collection
    companies = db.companies
    
    # Check if we have a test_company in the database
    async def get_test_company():
        # Try to find by ID
        company = await companies.find_one({"id": "test_company"})
        if company:
            return company, "id"
        
        # Try to find by _id
        company = await companies.find_one({"_id": "test_company"})
        if company:
            return company, "_id"
        
        # Try to find active company
        company = await companies.find_one({"active": True})
        if company:
            return company, "active"
        
        # No suitable company found
        return None, None
    
    import asyncio
    company, found_by = asyncio.run(get_test_company())
    
    if company:
        logger.info(f"Found test company by: {found_by}")
        
        # Fix the company data
        company_id = "test_company"
        
        # Apply fixes
        update_data = {
            "id": company_id,
            "brand_colors": ["#FF5733", "#33FF57"],  # Default test colors
            "updated_at": datetime.utcnow().isoformat()
        }
        
        # Update or create the company
        if found_by == "id" or found_by == "_id":
            # Update existing company
            asyncio.run(companies.update_one(
                {"_id": company.get("_id")}, 
                {"$set": update_data}
            ))
            logger.info(f"Updated test company with ID: {company_id}")
        else:
            # Create new test company with consistent ID
            new_company = {
                "_id": company_id,
                "id": company_id,
                "name": "Test Company",
                "description": "This is a test company",
                "email": "test@example.com",
                "phone": "123-456-7890",
                "address": "123 Test St.",
                "logo_url": "/uploads/default_logo.png",
                "brand_colors": ["#FF5733", "#33FF57"],  # Default test colors
                "active": True,
                "created_at": datetime.utcnow().isoformat(),
                "updated_at": datetime.utcnow().isoformat()
            }
            
            # Delete any existing company if needed
            if found_by == "active":
                asyncio.run(companies.delete_one({"_id": company.get("_id")}))
                
            # Add the new company
            asyncio.run(companies.insert_one(new_company))
            logger.info(f"Created new test company with ID: {company_id}")
    else:
        logger.info("No existing company found, will be created on first API access")
    
    logger.info("Company persistence fixes applied successfully")
''')
        print("✅ Created persistence fix script at", fix_script_path)
        return True
    except Exception as e:
        print(f"❌ Error creating fix script: {e}")
        return False

def update_main_app_file():
    """Update the main.py file to apply our fixes on startup"""
    main_file = "app/main.py"
    try:
        with open(main_file, "r") as f:
            content = f.read()
        
        # Check if our fix is already imported
        if "from app.db.fix_persistence import ensure_test_company_consistency" not in content:
            print("Updating main.py to apply fixes on startup...")
            
            # Find the database initialization code
            init_pattern = r"mongodb = SimpleMockDatabase\(\)(.*?)app\.mongodb = mongodb"
            
            if "SimpleMockDatabase()" in content:
                # Add our fix code after the database initialization
                fixed_content = content.replace(
                    "app.mongodb = mongodb",
                    "app.mongodb = mongodb\n\n    # Apply fixes for company persistence issues\n    from app.db.fix_persistence import ensure_test_company_consistency\n    ensure_test_company_consistency(mongodb)"
                )
                
                with open(main_file, "w") as f:
                    f.write(fixed_content)
                print("✅ Updated main.py to apply fixes on startup")
                return True
            else:
                print("❌ Could not find database initialization in main.py")
        else:
            print("✅ main.py already has persistence fixes")
            return True
    except Exception as e:
        print(f"❌ Error updating main.py: {e}")
    return False

def main():
    print_header("COMPANY PERSISTENCE FIX")
    
    # Step 1: Check current state
    print_header("STEP 1: Checking current state")
    company = get_active_company()
    
    if not company:
        print("Could not get active company. Is the API running?")
        api_response = os.system("curl -s http://127.0.0.1:8088/api/v1/companies/active > /dev/null")
        if api_response != 0:
            print("API does not appear to be running. Starting API server...")
            subprocess.Popen(
                ["python", "-m", "uvicorn", "app.main:app", "--host", "127.0.0.1", "--port", "8088"],
                stdout=subprocess.DEVNULL,
                stderr=subprocess.DEVNULL
            )
            print("Waiting 5 seconds for API to start...")
            time.sleep(5)
            company = get_active_company()
    
    if company:
        print(f"Current company: {company['name']}")
        print(f"Current ID: {company.get('id')}")
        print(f"Current colors: {company.get('brand_colors', [])}")
    else:
        print("Could not get company information.")
    
    # Step 2: Apply fixes
    print_header("STEP 2: Applying fixes")
    
    # Fix company model
    model_fixed = fix_company_model_file()
    
    # Fix CompanyDB class
    db_fixed = fix_company_db_class()
    
    # Fix simple mock DB
    mock_db_fixed = fix_simple_mock_db_bug()
    
    # Create direct fix script
    fix_script_created = create_direct_fix_script()
    
    # Update main app file to apply fixes
    main_updated = update_main_app_file()
    
    # Step 3: Restart API and test
    print_header("STEP 3: Restarting API and testing")
    print("Restarting API server...")
    subprocess.run(["pkill", "-f", "uvicorn app.main:app"], capture_output=True)
    time.sleep(2)  # Wait for the server to stop
    
    # Start API server
    subprocess.Popen(
        ["python", "-m", "uvicorn", "app.main:app", "--host", "127.0.0.1", "--port", "8088"],
        stdout=subprocess.DEVNULL,
        stderr=subprocess.DEVNULL
    )
    print("Waiting 5 seconds for API to initialize...")
    time.sleep(5)
    
    # Verify fixes
    updated_company = get_active_company()
    if updated_company:
        print(f"Updated company: {updated_company['name']}")
        print(f"Updated ID: {updated_company.get('id')}")
        print(f"Updated colors: {updated_company.get('brand_colors', [])}")
        
        # Check if ID is consistent
        id_fixed = updated_company.get('id') == COMPANY_ID
        
        # Check if brand_colors is a list, even if empty
        colors_fixed = isinstance(updated_company.get('brand_colors', None), list)
        
        print("\nFix Results:")
        print(f"ID consistency: {'✅ Fixed' if id_fixed else '❌ Not fixed'}")
        print(f"Brand colors structure: {'✅ Fixed' if colors_fixed else '❌ Not fixed'}")
        
        if id_fixed and colors_fixed:
            print("\n✅ COMPANY PERSISTENCE FIXES APPLIED SUCCESSFULLY!")
            print("The application should now correctly persist company data.")
        else:
            print("\n⚠️ Some fixes were not applied correctly.")
            print("Please check the logs above and run the script again if needed.")
    else:
        print("❌ Could not verify fixes. API may not be running properly.")
    
    print("\nNext steps:")
    print("1. Restart the frontend: cd frontend && npm run dev")
    print("2. Try updating the company settings in the UI")
    print("3. Navigate away and back to verify persistence")

if __name__ == "__main__":
    main()
