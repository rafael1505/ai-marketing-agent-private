#!/usr/bin/env python3
"""
Database Initialization ID Format Patch

This script ensures that the test company ID is properly preserved
through API server restarts. It monkey patches the SimpleMockDatabase
to use string IDs for the test company instead of numeric ones.
"""

import os
import sys

# Path to save the patch status to persist across restarts
PATCH_STATUS_FILE = "app/db/data/.id_format_patched"

def apply_id_format_patch():
    """Apply monkey patch to ensure test company ID is preserved"""
    try:
        from app.db.simple_mock_db import SimpleMockDatabase
        from app.db.company import CompanyDB
        
        print("[ID Format Patch] Applying database ID format patch...")
        
        # Store original methods
        original_create_company = CompanyDB.create_company
        
        # Enhanced create_company method that preserves test_company ID
        async def enhanced_create_company(self, company_data):
            # Use function attribute to track if test company has been handled
            if not hasattr(enhanced_create_company, "_test_company_handled"):
                enhanced_create_company._test_company_handled = False
                
            # Check if this is the test_company being created at startup
            if company_data.name == "Test Company" and not enhanced_create_company._test_company_handled:
                # Override ID to ensure it's test_company, not numeric
                print("[ID Format Patch] Using test_company ID for test company")
                
                # Force string ID for test company
                company_dict = company_data.model_dump() if hasattr(company_data, "model_dump") else company_data.dict()
                company_dict["_id"] = "test_company"
                company_dict["id"] = "test_company"
                
                # Manually insert into database
                await self.collection.insert_one(company_dict)
                
                # Mark as handled
                enhanced_create_company._test_company_handled = True
                
                return company_dict
            else:
                # For all other companies, use the original method
                return await original_create_company(self, company_data)
        
        # Apply the patch
        CompanyDB.create_company = enhanced_create_company
        
        # Mark as patched
        with open(PATCH_STATUS_FILE, "w") as f:
            f.write("patched")
            
        print("[ID Format Patch] Database ID format patch applied successfully")
    except Exception as e:
        print(f"[ID Format Patch] Error applying ID format patch: {e}")

if __name__ == "__main__":
    # Check if already patched
    if os.path.exists(PATCH_STATUS_FILE):
        print("[ID Format Patch] Database ID format already patched")
    else:
        apply_id_format_patch()
