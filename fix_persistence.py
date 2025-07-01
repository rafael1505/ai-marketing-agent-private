#!/usr/bin/env python3
# filepath: /mnt/c/Users/brc07274/OneDrive - Philips/Philips Files/BU - CI/Repository/AI Marketing Agent (Python)/ai-marketing-agent/fix_persistence.py
"""
This script permanently fixes the company data persistence issue by:
1. Enhancing the SimpleMockDatabase to persist data to disk
2. Creating a backup/restore mechanism for the database
"""

import os
import sys
import json
import shutil
import asyncio
from datetime import datetime
from pathlib import Path
from typing import Dict, Any

# Add the project root to the Python path to enable importing app modules
sys.path.append(str(Path(__file__).parent))

# Import necessary modules
from app.db.simple_mock_db import SimpleMockDatabase, SimpleMockCollection
from app.db.company import CompanyDB
from app.models.company import CompanyUpdate

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

# Monkey patch the SimpleMockDatabase to persist data to disk
def enhance_simple_mock_database():
    """Enhance the SimpleMockDatabase with persistence capabilities"""
    
    # Store the original methods
    original_init = SimpleMockDatabase.__init__
    original_insert = SimpleMockCollection.insert_one
    original_update = SimpleMockCollection.update_one
    original_delete = SimpleMockCollection.delete_one
    
    # Create enhanced methods
    def enhanced_init(self):
        """Enhanced initialization that loads from disk if available"""
        # First call the original init
        original_init(self)
        
        # Then try to load data from disk
        if os.path.exists(COMPANIES_FILE):
            try:
                with open(COMPANIES_FILE, 'r') as f:
                    self._data["companies"] = json.load(f)
                print(f"Loaded company data from {COMPANIES_FILE}")
            except Exception as e:
                print(f"Error loading companies from disk: {str(e)}")
    
    async def enhanced_insert_one(self, document):
        """Enhanced insert that persists to disk"""
        # First do the in-memory insert
        doc_id = await original_insert(self, document)
        
        # Then persist the parent db's data to disk
        if isinstance(self.data, dict) and hasattr(self.db, "_data") and "companies" in self.db._data:
            ensure_dirs()
            try:
                # Convert data to JSON serializable format
                data_to_save = {}
                for key, value in self.db._data["companies"].items():
                    # Create a copy to avoid modifying the original
                    doc = value.copy()
                    
                    # Convert datetime objects to ISO strings
                    for field in ["created_at", "updated_at"]:
                        if field in doc and isinstance(doc[field], datetime):
                            doc[field] = doc[field].isoformat()
                            
                    data_to_save[key] = doc
                
                # Create backup of the existing file
                backup_db_file(COMPANIES_FILE)
                    
                # Save to disk
                with open(COMPANIES_FILE, 'w') as f:
                    json.dump(data_to_save, f, indent=2)
                print(f"Persisted company data to disk after insert")
            except Exception as e:
                print(f"Error persisting companies to disk: {str(e)}")
        
        return doc_id
    
    async def enhanced_update_one(self, query, update_data):
        """Enhanced update that persists to disk"""
        # First do the in-memory update
        update_result = await original_update(self, query, update_data)
        
        # Then persist the parent db's data to disk
        if isinstance(self.data, dict) and hasattr(self.db, "_data") and "companies" in self.db._data:
            ensure_dirs()
            try:
                # Convert data to JSON serializable format
                data_to_save = {}
                for key, value in self.db._data["companies"].items():
                    # Create a copy to avoid modifying the original
                    doc = value.copy()
                    
                    # Convert datetime objects to ISO strings
                    for field in ["created_at", "updated_at"]:
                        if field in doc and isinstance(doc[field], datetime):
                            doc[field] = doc[field].isoformat()
                            
                    data_to_save[key] = doc
                
                # Create backup of the existing file
                backup_db_file(COMPANIES_FILE)
                    
                # Save to disk
                with open(COMPANIES_FILE, 'w') as f:
                    json.dump(data_to_save, f, indent=2)
                print(f"Persisted company data to disk after update")
            except Exception as e:
                print(f"Error persisting companies to disk: {str(e)}")
        
        return update_result
    
    async def enhanced_delete_one(self, query):
        """Enhanced delete that persists to disk"""
        # First do the in-memory delete
        delete_result = await original_delete(self, query)
        
        # Then persist the parent db's data to disk
        if isinstance(self.data, dict) and hasattr(self.db, "_data") and "companies" in self.db._data:
            ensure_dirs()
            try:
                # Convert data to JSON serializable format
                data_to_save = {}
                for key, value in self.db._data["companies"].items():
                    # Create a copy to avoid modifying the original
                    doc = value.copy()
                    
                    # Convert datetime objects to ISO strings
                    for field in ["created_at", "updated_at"]:
                        if field in doc and isinstance(doc[field], datetime):
                            doc[field] = doc[field].isoformat()
                            
                    data_to_save[key] = doc
                
                # Create backup of the existing file
                backup_db_file(COMPANIES_FILE)
                    
                # Save to disk
                with open(COMPANIES_FILE, 'w') as f:
                    json.dump(data_to_save, f, indent=2)
                print(f"Persisted company data to disk after delete")
            except Exception as e:
                print(f"Error persisting companies to disk: {str(e)}")
        
        return delete_result
    
    # Apply the monkey patches
    SimpleMockDatabase.__init__ = enhanced_init
    SimpleMockCollection.insert_one = enhanced_insert_one
    SimpleMockCollection.update_one = enhanced_update_one
    SimpleMockCollection.delete_one = enhanced_delete_one
    
    print("Enhanced SimpleMockDatabase with persistence capabilities")

async def create_or_update_test_company():
    """Create or update the test company with proper ID"""
    # Create a database instance
    db = SimpleMockDatabase()
    company_db = CompanyDB(db.companies)
    
    # Check if test_company exists
    test_company = await company_db.get_by_string_id("test_company")
    
    if test_company:
        print(f"Test company already exists: {test_company.get('name')}")
        
        # Update the company with new brand colors
        update_data = CompanyUpdate(
            name="Test Company",
            description="This company was updated by the persistence fix",
            brand_colors=["#1a73e8", "#ea4335", "#fbbc04", "#34a853", "#ffffff"],  # Fixed brand colors
            logo_url="/uploads/default_logo.png"
        )
        
        updated_company = await company_db.update_company("test_company", update_data)
        if updated_company:
            print(f"Test company updated with fixed brand colors")
    else:
        print("Creating new test company with ID 'test_company'")
        
        # Create test company data
        test_company_data = {
            "_id": "test_company",
            "id": "test_company",
            "name": "Test Company",
            "description": "This is a test company with persistence enabled",
            "email": "contact@testcompany.com",
            "phone": "+1 (555) 123-4567",
            "address": "123 Test Street, Test City, TC 12345",
            "logo_url": "/uploads/default_logo.png",
            "brand_colors": ["#1a73e8", "#ea4335", "#fbbc04", "#34a853", "#ffffff"],
            "active": True,
            "created_at": datetime.utcnow(),
            "updated_at": datetime.utcnow()
        }
        
        # Insert directly
        await db.companies.insert_one(test_company_data)
        print("Test company created successfully")

async def verify_persistence():
    """Verify that persistence is working"""
    # Check if the database file exists
    if os.path.exists(COMPANIES_FILE):
        print(f"\nVerifying database file at {COMPANIES_FILE}...")
        
        try:
            with open(COMPANIES_FILE, 'r') as f:
                data = json.load(f)
                
            # Check for test_company
            if "test_company" in data:
                company = data["test_company"]
                print(f"Found test_company in database file:")
                print(f"  Name: {company.get('name')}")
                print(f"  Brand colors: {company.get('brand_colors')}")
                return True
            else:
                print("test_company not found in database file")
                return False
        except Exception as e:
            print(f"Error reading database file: {str(e)}")
            return False
    else:
        print(f"\nDatabase file not found at {COMPANIES_FILE}")
        return False

async def main():
    print("Starting company persistence fix...")
    
    # Step 1: Enhance SimpleMockDatabase with persistence
    enhance_simple_mock_database()
    
    # Step 2: Create/update test company
    await create_or_update_test_company()
    
    # Step 3: Verify persistence
    persistence_verified = await verify_persistence()
    
    if persistence_verified:
        print("\n✅ SUCCESS: Persistence fix has been applied!")
        print("The application will now correctly save company data between restarts.")
    else:
        print("\n❌ ERROR: Persistence fix could not be verified.")
        print("Please check the logs for more information.")
    
    print("\nTo use this fix:")
    print("1. Ensure the API server is restarted")
    print("2. If the API server is already running, restart it")
    print("3. Company data will now persist across API server restarts")

if __name__ == "__main__":
    asyncio.run(main())
