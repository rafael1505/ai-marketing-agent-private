#!/usr/bin/env python3
# filepath: /mnt/c/Users/brc07274/OneDrive - Philips/Philips Files/BU - CI/Repository/AI Marketing Agent (Python)/ai-marketing-agent/app/core/persistence_patch.py
"""
This module automatically enhances the SimpleMockDatabase with persistence capabilities
It's designed to be imported at application startup to ensure data is loaded from disk
"""

import os
import json
import shutil
from datetime import datetime
from typing import Dict, Any

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
    print(f"[DB Persistence] Created backup: {backup_path}")

def apply_persistence_patch():
    """Apply the persistence patch to SimpleMockDatabase"""
    from app.db.simple_mock_db import SimpleMockDatabase, SimpleMockCollection
    
    print("[DB Persistence] Applying database persistence patch...")
    
    # Store the original methods
    original_init = SimpleMockDatabase.__init__
    original_insert = SimpleMockCollection.insert_one
    original_update = SimpleMockCollection.update_one
    original_delete = SimpleMockCollection.delete_one
    original_find_one = SimpleMockCollection.find_one  # Also store the original find_one method
    
    # Create enhanced methods
    def enhanced_init(self):
        """Enhanced initialization that loads from disk if available"""
        # First call the original init
        original_init(self)
        
        # Then try to load data from disk
        ensure_dirs()
        if os.path.exists(COMPANIES_FILE):
            try:
                with open(COMPANIES_FILE, 'r') as f:
                    companies_data = json.load(f)
                    self._data["companies"] = companies_data
                print(f"[DB Persistence] Loaded company data from {COMPANIES_FILE}")
                print(f"[DB Persistence] Found {len(companies_data)} companies")
            except Exception as e:
                print(f"[DB Persistence] Error loading companies from disk: {str(e)}")
    
    async def enhanced_insert_one(self, document):
        """Enhanced insert that persists to disk"""
        # First do the in-memory insert
        doc_id = await original_insert(self, document)
        
        # Then persist the parent db's data to disk if it's the companies collection
        collection_key = None
        for key, collection in self.db._data.items():
            if collection is self.data:
                collection_key = key
                break
                
        if collection_key == "companies":
            ensure_dirs()
            try:
                # Convert data to JSON serializable format
                data_to_save = {}
                for key, value in self.data.items():
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
                print(f"[DB Persistence] Persisted company data to disk after insert")
            except Exception as e:
                print(f"[DB Persistence] Error persisting companies to disk: {str(e)}")
        
        return doc_id
    
    async def enhanced_update_one(self, query, update_data):
        """Enhanced update that persists to disk"""
        # First do the in-memory update
        update_result = await original_update(self, query, update_data)
        
        # Then persist the parent db's data to disk if it's the companies collection
        collection_key = None
        for key, collection in self.db._data.items():
            if collection is self.data:
                collection_key = key
                break
                
        if collection_key == "companies":
            ensure_dirs()
            try:
                # Convert data to JSON serializable format
                data_to_save = {}
                for key, value in self.data.items():
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
                print(f"[DB Persistence] Persisted company data to disk after update")
            except Exception as e:
                print(f"[DB Persistence] Error persisting companies to disk: {str(e)}")
        
        return update_result
    
    async def enhanced_delete_one(self, query):
        """Enhanced delete that persists to disk"""
        # First do the in-memory delete
        delete_result = await original_delete(self, query)
        
        # Then persist the parent db's data to disk if it's the companies collection
        collection_key = None
        for key, collection in self.db._data.items():
            if collection is self.data:
                collection_key = key
                break
                
        if collection_key == "companies":
            ensure_dirs()
            try:
                # Convert data to JSON serializable format
                data_to_save = {}
                for key, value in self.data.items():
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
                print(f"[DB Persistence] Persisted company data to disk after delete")
            except Exception as e:
                print(f"[DB Persistence] Error persisting companies to disk: {str(e)}")
        
        return delete_result
    
    # Define enhanced find_one method to always read the latest from disk for companies
    async def enhanced_find_one(self, query=None):
        """Enhanced find_one method that reloads from disk for companies collection"""
        collection_key = None
        for key, collection in self.db._data.items():
            if collection is self.data:
                collection_key = key
                break
                
        # Special handling for companies collection to ensure freshness
        if collection_key == "companies":
            # Reload from disk for every read to ensure we have the latest data
            if os.path.exists(COMPANIES_FILE):
                try:
                    with open(COMPANIES_FILE, 'r') as f:
                        companies_data = json.load(f)
                        # Update in-memory data
                        self.db._data["companies"] = companies_data
                except Exception as e:
                    print(f"[DB Persistence] Warning: Could not refresh companies from disk: {str(e)}")
        
        # Now call the original method with the freshly loaded data
        return await original_find_one(self, query)
        
    # Apply the monkey patches
    SimpleMockDatabase.__init__ = enhanced_init
    SimpleMockCollection.insert_one = enhanced_insert_one
    SimpleMockCollection.update_one = enhanced_update_one
    SimpleMockCollection.delete_one = enhanced_delete_one
    SimpleMockCollection.find_one = enhanced_find_one  # Add the enhanced find_one
    
    print("[DB Persistence] Database persistence patch applied successfully")

# Apply the patch when this module is imported
apply_persistence_patch()
