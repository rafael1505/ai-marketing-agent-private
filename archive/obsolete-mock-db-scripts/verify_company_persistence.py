#!/usr/bin/env python3
"""
Company Persistence Verification Tool

This tool verifies and fixes company persistence issues in the database.
It checks the company ID formats, brand_colors array handling, and other 
potential issues with data storage. It also includes a direct verification
of API persistence by updating the database and checking the API response.

Usage: python verify_company_persistence.py [options]

Options:
    --fix          Apply fixes to the database (default: just report issues)
    --verbose      Show detailed information
    --direct-test  Perform a direct test by updating DB and checking API
    --restart-api  Restart the API server as part of testing
"""

import asyncio
import sys
import os
import json
import requests
import time
import subprocess
from datetime import datetime
from typing import Dict, Any, List, Optional

# Import app modules
try:
    from app.db.simple_mock_db import SimpleMockDatabase
    from app.db.company import CompanyDB
    from app.models.company import CompanyUpdate
except ImportError:
    print("Error: Unable to import required modules.")
    print("Make sure you're running this script from the project root directory.")
    sys.exit(1)

# Parse command line arguments
APPLY_FIXES = "--fix" in sys.argv
VERBOSE = "--verbose" in sys.argv or "-v" in sys.argv
DIRECT_TEST = "--direct-test" in sys.argv
RESTART_API = "--restart-api" in sys.argv

# Path for storing database files
DB_DIR = os.path.join(os.getcwd(), "app", "db", "data")
COMPANIES_FILE = os.path.join(DB_DIR, "companies.json")
API_URL = "http://localhost:8088"

class CompanyValidator:
    def __init__(self):
        self.mock_db = SimpleMockDatabase()
        self.company_db = CompanyDB(self.mock_db.companies)
        self.issues = []
        self.fixes = []
    
    async def get_all_companies(self) -> List[Dict[str, Any]]:
        """Get all companies from the database."""
        return await self.mock_db.companies.find({})
    
    async def check_company_id_format(self, company: Dict[str, Any]) -> bool:
        """Check if company has proper ID fields."""
        issues = []
        
        # Check if _id exists
        if "_id" not in company:
            issues.append(f"Company '{company.get('name', 'Unknown')}' missing _id field")
        
        # Check if id exists
        if "id" not in company:
            issues.append(f"Company '{company.get('name', 'Unknown')}' missing id field")
        
        # Check if id and _id match for string IDs
        if isinstance(company.get("_id"), str) and company.get("id") != company.get("_id"):
            issues.append(
                f"Company ID mismatch: _id='{company.get('_id')}', id='{company.get('id')}'"
            )
        
        # Check special case for test_company
        if company.get("id") == "test_company" or company.get("_id") == "test_company":
            if company.get("id") != "test_company" or company.get("_id") != "test_company":
                issues.append("test_company ID inconsistency detected")
        
        # Add issues to the main list
        if issues:
            self.issues.extend(issues)
            return False
        return True
    
    async def check_brand_colors_format(self, company: Dict[str, Any]) -> bool:
        """Check if brand_colors is properly formatted as a list."""
        issues = []
        
        # Check if brand_colors exists
        if "brand_colors" not in company:
            issues.append(f"Company '{company.get('name', 'Unknown')}' missing brand_colors field")
        
        # Check if brand_colors is a list
        elif not isinstance(company.get("brand_colors"), list):
            issues.append(
                f"Company '{company.get('name', 'Unknown')}' brand_colors is not a list: "
                f"{type(company.get('brand_colors')).__name__}"
            )
        
        # Check if brand_colors is empty when it shouldn't be
        elif len(company.get("brand_colors", [])) == 0:
            issues.append(f"Company '{company.get('name', 'Unknown')}' has empty brand_colors")
        
        # Add issues to the main list
        if issues:
            self.issues.extend(issues)
            return False
        return True
    
    async def check_active_company(self) -> Optional[Dict[str, Any]]:
        """Check if there's an active company."""
        active = await self.company_db.get_active_company()
        if not active:
            self.issues.append("No active company found in database")
            return None
        
        if VERBOSE:
            print(f"Active company: {active.get('name')} (ID: {active.get('id')})")
        
        return active
    
    async def fix_company_id_format(self, company: Dict[str, Any]) -> Dict[str, Any]:
        """Fix company ID format issues."""
        company_id = company.get("id") or company.get("_id")
        if not company_id:
            # Generate a new ID if neither exists
            company_id = f"company_{len(self.fixes) + 1}"
        
        # Create a fixed company with consistent ID fields
        fixed = {**company, "_id": company_id, "id": company_id}
        
        # Update the document in the database
        if APPLY_FIXES:
            # Delete the old document
            await self.mock_db.companies.delete_one({"_id": company.get("_id")})
            # Insert the fixed document
            await self.mock_db.companies.insert_one(fixed)
            self.fixes.append(f"Fixed ID format for company '{fixed.get('name')}'")
        
        return fixed
    
    async def fix_brand_colors_format(self, company: Dict[str, Any]) -> Dict[str, Any]:
        """Fix brand_colors format issues."""
        colors = company.get("brand_colors")
        
        if colors is None:
            # Default colors if missing
            colors = ["#3B82F6", "#A855F7"]
        elif not isinstance(colors, list):
            # Convert to list if not already
            if isinstance(colors, str):
                colors = [colors]
            else:
                # Default colors if can't convert
                colors = ["#3B82F6", "#A855F7"]
        elif len(colors) == 0:
            # Add default colors if empty
            colors = ["#3B82F6", "#A855F7"]
        
        # Create a fixed company with proper brand_colors
        fixed = {**company, "brand_colors": colors}
        
        # Update the document in the database
        if APPLY_FIXES:
            await self.mock_db.companies.update_one(
                {"_id": company.get("_id")},
                {"$set": {"brand_colors": colors}}
            )
            self.fixes.append(f"Fixed brand_colors for company '{fixed.get('name')}'")
        
        return fixed
    
    async def ensure_test_company_exists(self) -> Dict[str, Any]:
        """Ensure test_company exists with proper configuration."""
        # Check if test_company already exists
        test_company = await self.company_db.get_company("test_company")
        
        if test_company:
            # Fix any issues with the existing test_company
            id_ok = await self.check_company_id_format(test_company)
            colors_ok = await self.check_brand_colors_format(test_company)
            
            if not id_ok:
                test_company = await self.fix_company_id_format(test_company)
            
            if not colors_ok:
                test_company = await self.fix_brand_colors_format(test_company)
            
            # Make sure it's active
            if not test_company.get("active"):
                if APPLY_FIXES:
                    await self.mock_db.companies.update_one(
                        {"_id": "test_company"},
                        {"$set": {"active": True}}
                    )
                    self.fixes.append("Made test_company active")
                test_company["active"] = True
        else:
            # Create a new test_company
            test_company = {
                "_id": "test_company",
                "id": "test_company",
                "name": "Test Company",
                "description": "This is a test company for development",
                "email": "contact@testcompany.com",
                "phone": "+1 (555) 123-4567",
                "address": "123 Test Street, Test City, TC 12345",
                "logo_url": "/uploads/default_logo.png",
                "brand_colors": ["#3B82F6", "#A855F7"],
                "active": True,
                "created_at": datetime.utcnow(),
                "updated_at": datetime.utcnow()
            }
            
            if APPLY_FIXES:
                await self.mock_db.companies.insert_one(test_company)
                self.fixes.append("Created new test_company")
        
        return test_company
    
    async def run_verification(self):
        """Run the full verification process."""
        print("=== Company Persistence Verification ===")
        print(f"Fix mode: {'ENABLED' if APPLY_FIXES else 'DISABLED'}")
        
        # Debug output of the raw database contents
        print("\nRaw database contents:")
        for id_key, company_data in self.mock_db._data["companies"].items():
            print(f"ID: {id_key}, Name: {company_data.get('name', 'Unknown')}")
        
        # 1. Check for active company
        active_company = await self.check_active_company()
        
        # 2. Check all companies
        companies = await self.get_all_companies()
        print(f"\nFound {len(companies)} companies in database")
        
        for company in companies:
            if VERBOSE:
                print(f"\nChecking company: {company.get('name')} ({company.get('_id')})")
            
            await self.check_company_id_format(company)
            await self.check_brand_colors_format(company)
        
        # 3. Ensure test_company exists
        test_company = await self.ensure_test_company_exists()
        
        # 4. Report issues and fixes
        print("\n=== Verification Results ===")
        
        if self.issues:
            print(f"\nFound {len(self.issues)} issues:")
            for i, issue in enumerate(self.issues, 1):
                print(f"{i}. {issue}")
        else:
            print("\n✅ No issues found! Database appears to be properly configured.")
        
        if APPLY_FIXES and self.fixes:
            print(f"\nApplied {len(self.fixes)} fixes:")
            for i, fix in enumerate(self.fixes, 1):
                print(f"{i}. {fix}")
        
        # 5. Final verification
        if APPLY_FIXES and self.issues:
            # Re-check after fixes
            self.issues = []
            companies = await self.get_all_companies()
            
            print("\n=== Verification After Fixes ===")
            
            for company in companies:
                await self.check_company_id_format(company)
                await self.check_brand_colors_format(company)
            
            if self.issues:
                print(f"\n⚠️ {len(self.issues)} issues remain after fixes:")
                for i, issue in enumerate(self.issues, 1):
                    print(f"{i}. {issue}")
            else:
                print("\n🎉 All issues fixed successfully!")
        
        # 6. Test updating test_company
        if APPLY_FIXES:
            print("\n=== Testing Company Update ===")
            try:
                # Update test_company
                update = CompanyUpdate(
                    name="Verified Test Company",
                    description="This company was verified and fixed",
                    brand_colors=["#AA0000", "#00AA00", "#0000AA"]
                )
                
                updated = await self.company_db.update_company("test_company", update)
                if updated:
                    print("✅ Company update successful")
                    
                    # Verify update persistence
                    verify = await self.company_db.get_company("test_company")
                    if verify:
                        name_match = verify.get('name') == update.name
                        colors_match = sorted(verify.get('brand_colors', [])) == sorted(update.brand_colors)
                        
                        print(f"Name updated correctly: {'✅' if name_match else '❌'}")
                        print(f"Colors updated correctly: {'✅' if colors_match else '❌'}")
                        
                        if name_match and colors_match:
                            print("\n🎉 Company persistence is fully functional at database level!")
                else:
                    print("❌ Company update failed")
            except Exception as e:
                print(f"❌ Error during update test: {e}")

# Add these functions at the end for direct API testing

def ensure_dirs():
    """Ensure the database directories exist"""
    os.makedirs(DB_DIR, exist_ok=True)

def load_companies_from_file():
    """Load company data from the file"""
    ensure_dirs()
    if not os.path.exists(COMPANIES_FILE):
        print(f"Database file not found: {COMPANIES_FILE}")
        return {}
        
    try:
        with open(COMPANIES_FILE, 'r') as f:
            data = json.load(f)
            print(f"Loaded {len(data)} companies from database file")
            return data
    except Exception as e:
        print(f"Error loading companies: {str(e)}")
        return {}

def save_companies_to_file(data):
    """Save company data to the file"""
    ensure_dirs()
    
    try:
        # Create backup
        if os.path.exists(COMPANIES_FILE):
            backup_dir = os.path.join(DB_DIR, "backups")
            os.makedirs(backup_dir, exist_ok=True)
            timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
            backup_file = os.path.join(backup_dir, f"companies.json.{timestamp}")
            with open(COMPANIES_FILE, 'r') as src, open(backup_file, 'w') as dest:
                dest.write(src.read())
                
        # Save new data
        with open(COMPANIES_FILE, 'w') as f:
            json.dump(data, f, indent=2)
        print(f"Saved {len(data)} companies to database file")
        return True
    except Exception as e:
        print(f"Error saving companies: {str(e)}")
        return False

def update_test_company_directly():
    """Update the test company directly in the file with unique brand colors for this session"""
    companies = load_companies_from_file()
    
    # Create timestamp for uniqueness
    timestamp = datetime.now().strftime("%Y%m%d%H%M%S")
    
    # Find the active company or the test company
    updated = False
    for key, company in companies.items():
        if company.get("active") or key == "test_company" or company.get("_id") == "test_company":
            # Update with unique brand colors
            company["brand_colors"] = [f"#FF0000", f"#00FF00", f"#0000FF", f"#{timestamp}"]
            company["description"] = f"Updated by verify script at {timestamp}"
            company["updated_at"] = datetime.now().isoformat()
            print(f"Updated company {key} with unique brand colors")
            
            # Make sure we have proper ID fields
            if "_id" not in company or company["_id"] != "test_company":
                company["_id"] = "test_company"
            if "id" not in company or company["id"] != "test_company":
                company["id"] = "test_company"
            
            # Make sure active is set
            company["active"] = True
                
            updated = True
            save_companies_to_file(companies)
            return company
    
    if not updated:
        print("No suitable company found to update")
    return None

def check_api_company():
    """Check if the API returns the correct company data"""
    try:
        response = requests.get(f"{API_URL}/api/v1/companies/active")
        if response.status_code == 200:
            company = response.json()
            print(f"API returned company: {company.get('name')}")
            print(f"Description: {company.get('description')}")
            print(f"Brand colors: {company.get('brand_colors')}")
            return company
        else:
            print(f"API error: {response.status_code} - {response.text}")
            return None
    except Exception as e:
        print(f"Error calling API: {str(e)}")
        return None

def restart_api_server():
    """Restart the API server to test persistence"""
    print("\nRestarting API server...")
    
    # Use the restart script
    try:
        subprocess.run(["./restart_api_clean.sh"], check=True)
        # Give it time to start
        time.sleep(3)
        print("API server restarted")
    except Exception as e:
        print(f"Error restarting API server: {str(e)}")

def run_direct_test():
    """Run direct test by updating company in file and checking API"""
    print("\n============================================")
    print("Direct API Persistence Test")
    print("============================================\n")
    
    # Step 1: Check current company data from API
    print("Step 1: Checking current company data from API...")
    original_company = check_api_company()
    
    # Step 2: Update company directly in database file
    print("\nStep 2: Updating company directly in database file...")
    updated_company = update_test_company_directly()
    
    # Step 3: Restart API server if requested
    if RESTART_API:
        print("\nStep 3: Restarting API server...")
        restart_api_server()
    
    # Step 4: Check if API returns updated data
    print("\nStep 4: Checking if API returns updated company data...")
    new_company = check_api_company()
    
    # Step 5: Verify persistence
    print("\nStep 5: Verifying persistence...")
    if not new_company:
        print("❌ Failed: Couldn't get company data from API after update")
        return
        
    if updated_company and new_company:
        if set(new_company.get("brand_colors", [])) == set(updated_company.get("brand_colors", [])):
            print("✅ Success: Brand colors persisted correctly!")
        else:
            print("❌ Failed: Brand colors don't match")
            print(f"Expected: {updated_company.get('brand_colors')}")
            print(f"Actual: {new_company.get('brand_colors')}")
            
        if new_company.get("description") == updated_company.get("description"):
            print("✅ Success: Description persisted correctly!")
        else:
            print("❌ Failed: Description doesn't match")
            print(f"Expected: {updated_company.get('description')}")
            print(f"Actual: {new_company.get('description')}")
            
        # Additional check for test_company ID
        test_company_id = new_company.get("id") == "test_company"
        if test_company_id:
            print("✅ Success: Company has correct ID (test_company)!")
        else:
            print(f"❌ Note: Company doesn't have test_company ID (has: {new_company.get('id')})")
            
    else:
        print("❌ Failed: Missing company data to compare")
    
    print("\n============================================")
    print("Direct test complete")
    print("============================================")

# Modify the main function to include direct testing
if __name__ == "__main__":
    if DIRECT_TEST:
        run_direct_test()
    else:
        validator = CompanyValidator()
        asyncio.run(validator.run_verification())
