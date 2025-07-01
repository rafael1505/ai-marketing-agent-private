"""
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
