from fastapi import FastAPI, Request
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import JSONResponse
from motor.motor_asyncio import AsyncIOMotorClient
import logging
import os
import traceback
import json
from datetime import datetime
from app.core.config import settings
from app.api.v1.api import api_router
from app.core.i18n import setup_i18n

# Configure logging
logging.basicConfig(level=logging.DEBUG, 
                   format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
                   handlers=[logging.StreamHandler()])

# Setup development mode flag - always use mock DB for local development
USE_MOCK_DB = True  # Force using mock database for development

# Use a different name for the FastAPI app to avoid confusion with the app package
api_app = FastAPI(
    title=settings.PROJECT_NAME,
    version=settings.PROJECT_VERSION,
    description="AI Marketing Agent API"
)

# Set up CORS
cors_origins = settings.CORS_ORIGINS if isinstance(settings.CORS_ORIGINS, list) else [origin.strip() for origin in settings.CORS_ORIGINS.split(",")]
# Explicitly add frontend origins for development
cors_origins.extend([
    "http://localhost:3000", 
    "http://localhost:3001", 
    "http://127.0.0.1:3000", 
    "http://127.0.0.1:3001"
])
logging.info(f"CORS origins: {cors_origins}")

api_app.add_middleware(
    CORSMiddleware,
    allow_origins=cors_origins,
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Import and apply FormData array parsing fix 
# This also includes special handling for multipart/form-data without boundary
from app.core.formdata_array_fix import apply_array_parsing_fix
apply_array_parsing_fix(api_app)

# Import and apply database persistence patch
from app.core.persistence_patch import apply_persistence_patch
# Import and apply ID format patch
import app.db.id_format_patch
apply_persistence_patch()
logging.info("Database persistence patch has been applied")

@api_app.on_event("startup")
async def startup_db_client():
    # Set up mock database for development
    from app.db.simple_mock_db import SimpleMockDatabase
    api_app.mongodb_client = SimpleMockDatabase()
    api_app.mongodb = api_app.mongodb_client
    logging.info("Using simple mock database for development")
    
    setup_i18n()
    
    # Initialize the test company
    try:
        # Initialize test data
        from app.core.auth import get_password_hash
        from datetime import datetime
        from app.db.company import CompanyDB
        from app.models.company import CompanyCreate, CompanyUpdate
        
        # Use the correct way to access collections from MockDatabase
        users_collection = api_app.mongodb.users

        # Clear existing users to avoid duplication
        try:
            # Pass a query dictionary to delete_many
            await users_collection.delete_many({"email": "test@example.com"})
        except Exception as e:
            logging.warning(f"Could not clear test user, may not exist: {e}")
        # Create test user with all required fields
        test_user = {
            # "_id": ObjectId(), # ObjectId might not be compatible with SQLite mock or necessary
            "name": "Test User",
            "full_name": "Test User",
            "email": "test@example.com",
            "hashed_password": "$2b$12$KEM/.wsdaeBqeOSyN8gVAubF.uyCe21l4cF5zdTCLlYtsMkpVd8Be", # Corrected hash
            "active": True,
            "is_admin": True,
            "company_id": "test_company",
            "created_at": datetime.utcnow().isoformat(), # Store as ISO format string
            "updated_at": datetime.utcnow().isoformat()  # Store as ISO format string
        }
        
        # Insert test user into collection
        await users_collection.insert_one(test_user)
          # Debug: Try to retrieve the user
        test_fetch = await users_collection.find_one({"email": "test@example.com"})
        if test_fetch:
            logging.info(f"Test user found: {test_fetch}")
        else:
            logging.error("Failed to retrieve test user after creation")
            
        logging.info("Test user created successfully: test@example.com")
        
        # Create test company only if no companies exist
        try:
            # Access the companies collection
            companies_collection = api_app.mongodb.companies
            
            # Check if we have any companies already (from persistence)
            # Be explicit about checking the collection directly
            all_companies = []
            try:
                # Get companies cursor
                companies_cursor = companies_collection.find({})
                
                # Handle both async and sync cases
                if hasattr(companies_cursor, '__await__'):
                    try:
                        # For real MongoDB
                        all_companies = await companies_cursor
                    except Exception as e:
                        # For our mock cursor
                        all_companies = list(companies_cursor)
                else:
                    # For direct list results or other types
                    all_companies = list(companies_cursor)
                
                # Get the count
                existing_count = len(all_companies)
                logging.info(f"Database loaded with {existing_count} companies")
                
                # Debug: print company info
                for company in all_companies:
                    logging.info(f"Found company: {company.get('name')}, ID: {company.get('_id')}, "
                                f"active: {company.get('active')}, "
                                f"brand_colors: {company.get('brand_colors')}")
            except Exception as e:
                logging.error(f"Error checking existing companies: {e}")
                existing_count = 0
            
            if existing_count > 0:
                logging.info(f"Found {existing_count} existing companies - skipping test company creation")
                
                # Make sure one company is set as active 
                active_company = None
                try:
                    active_company = await companies_collection.find_one({"active": True})
                except Exception as e:
                    logging.error(f"Error finding active company: {e}")
                
                if not active_company:
                    logging.info("No active company found - setting the first company as active")
                    first_company = all_companies[0]
                    try:
                        await companies_collection.update_one(
                            {"_id": first_company.get("_id")},
                            {"$set": {"active": True}}
                        )
                        logging.info(f"Set company {first_company.get('name')} as active")
                    except Exception as e:
                        logging.error(f"Error setting company as active: {e}")
            else:
                # No companies found, create the test company
                logging.info("No existing companies found - creating test company")
                
                # Create a test company
                test_company = {
                    "_id": "test_company",  # Use _id instead of id to match MongoDB expectations
                    "id": "test_company",   # Explicitly add the id field to match both ways
                    "name": "Test Company",
                    "description": "This is a test company for development",
                    "email": "contact@testcompany.com",
                    "phone": "+1 (555) 123-4567",
                    "address": "123 Test Street, Test City, TC 12345",
                    "brand_colors": ["#FF0000", "#00FF00", "#0000FF"],  # Initialize with default colors
                    "active": True,
                    "created_at": datetime.utcnow().isoformat(),
                    "updated_at": datetime.utcnow().isoformat()
                }
                
                # Insert test company into collection
                await companies_collection.insert_one(test_company)
                
                # Verify company was created
                test_company_fetch = await companies_collection.find_one({"name": "Test Company"})
                if test_company_fetch:
                    logging.info(f"Test company found: {test_company_fetch}")
                else:
                    logging.error("Failed to retrieve test company after creation")
                    
                logging.info("Test company created successfully: Test Company")
        except Exception as e:
            logging.error(f"Error creating test company: {e}")
    except Exception as e:
        logging.error(f"Error creating test user: {e}")

@api_app.on_event("shutdown")
async def shutdown_db_client():
    api_app.mongodb_client.close()

@api_app.exception_handler(Exception)
async def global_exception_handler(request: Request, exc: Exception):
    error_detail = {
        "error": str(exc),
        "traceback": traceback.format_exc()
    }
    logging.error(f"Exception occurred: {error_detail}")
    return JSONResponse(
        status_code=500,
        content=error_detail
    )

# Add direct routes for API debugging
from app.api.v1 import companies

# Include main API router
api_app.include_router(api_router, prefix="/api/v1")

# Add special debug routes for direct access
from fastapi import APIRouter, Depends, HTTPException, Request
from datetime import datetime
import traceback

api_debug_router = APIRouter(prefix="/api-debug", tags=["api-debug"])

@api_debug_router.get("/{company_id}")
async def get_company_debug(company_id: str, request: Request):
    """Debug endpoint to directly get company by ID without authentication"""
    try:
        mongodb = request.app.mongodb
        company_db = companies.CompanyDB(mongodb.companies)
        
        # Log the attempt
        logging.info(f"Debug API: Attempting to get company with ID: {company_id}")
        
        # Try both methods to find the company
        if company_id == "test_company":
            company = await company_db.get_by_string_id(company_id)
            logging.info(f"Debug API: Using string ID lookup for test_company: {company is not None}")
        else:
            company = await company_db.get(company_id)
            logging.info(f"Debug API: Using regular ID lookup: {company is not None}")
            
        if not company and company_id == "test_company":
            # Fallback: search by "id" field
            logging.info("Debug API: Trying fallback lookup by id field")
            company = await mongodb.companies.find_one({"id": company_id})
            logging.info(f"Debug API: Fallback result: {company is not None}")
        
        if not company:
            logging.error(f"Debug API: Company not found with ID: {company_id}")
            raise HTTPException(status_code=404, detail="Company not found")
            
        logging.info(f"Debug API: Successfully found company: {company.get('name')}")
        return company
    except Exception as e:
        logging.error(f"Debug API error: {str(e)}")
        raise HTTPException(status_code=500, detail=f"Error retrieving company: {str(e)}")

@api_debug_router.put("/{company_id}")
async def update_company_debug(company_id: str, request: Request):
    """Debug endpoint to directly update company by ID without authentication"""
    try:
        # Parse the JSON body
        json_data = await request.json()
        logging.info(f"Debug update for company {company_id}: {json_data}")
        
        # Get the company DB
        mongodb = request.app.mongodb
        company_db = companies.CompanyDB(mongodb.companies)
        
        # Handle brand_colors properly - ensure it's always a list
        if "brand_colors" in json_data:
            if json_data["brand_colors"] is None:
                json_data["brand_colors"] = []
            elif not isinstance(json_data["brand_colors"], list):
                # Try to convert to list if it's not already
                try:
                    json_data["brand_colors"] = list(json_data["brand_colors"])
                except:
                    json_data["brand_colors"] = []
            
            logging.info(f"Processed brand_colors: {json_data['brand_colors']}")
        
        # Convert to CompanyUpdate model
        from app.models.company import CompanyUpdate
        company_update = companies.parse_obj_as(CompanyUpdate, json_data)
        
        # Special handling for test_company
        if company_id == "test_company":
            # Try to find the active company first
            active_company = await company_db.get_active_company()
            if active_company:
                real_id = active_company.get("_id", company_id)
                logging.info(f"Found active company with ID: {real_id}")
                
                # Special case for updating test_company directly
                if "brand_colors" in json_data:
                    logging.info(f"Setting brand_colors to: {json_data['brand_colors']}")
                
                # Update directly in the collection to bypass potential ID issues
                # Make sure we have the correct _id field set
                query = {"$or": [
                    {"_id": "test_company"},
                    {"id": "test_company"},
                    {"active": True}
                ]}
                
                update_result = await mongodb.companies.update_one(
                    query,
                    {"$set": {
                        **{k: v for k, v in json_data.items() if k != "id"},
                        "updated_at": datetime.utcnow().isoformat(),
                        # Make sure _id and id match to prevent confusion
                        "_id": "test_company",
                        "id": "test_company"
                    }}
                )
                
                if update_result.matched_count > 0:
                    # Get the updated company
                    updated_company = await company_db.get_by_string_id("test_company")
                    if not updated_company:
                        updated_company = await company_db.get_active_company()
                    logging.info(f"Company updated successfully via direct method: {updated_company}")
                    return updated_company
            else:
                logging.error(f"No active company found to update")
                raise HTTPException(status_code=404, detail="No active company found")
        
        # Standard update path
        updated_company = await company_db.update_company(company_id, company_update)
        if not updated_company:
            logging.error(f"Company not found: {company_id}")
            raise HTTPException(status_code=404, detail=f"Company not found: {company_id}")
        
        logging.info(f"Company updated successfully: {updated_company}")
        return updated_company
    except Exception as e:
        logging.error(f"Error updating company: {str(e)}")
        logging.error(f"Exception traceback: {traceback.format_exc()}")
        
        # For debugging, try a direct update to the database instead
        try:
            logging.info("Trying direct database update as fallback...")
            mongodb = request.app.mongodb
            
            # Make a simple update with minimal fields
            simple_data = {
                "name": json_data.get("name", "Updated Company"),
                "description": json_data.get("description", ""),
                "brand_colors": json_data.get("brand_colors", []),
                "updated_at": datetime.utcnow().isoformat()
            }
            
            # Try updating the active company directly
            await mongodb.companies.update_one(
                {"active": True},
                {"$set": simple_data}
            )
            
            # Return the active company
            company_db = companies.CompanyDB(mongodb.companies)
            result = await company_db.get_active_company()
            if result:
                logging.info(f"Fallback update succeeded: {result}")
                return result
        except Exception as fallback_error:
            logging.error(f"Fallback update failed: {str(fallback_error)}")
            
        # If all else fails, return the original error
        raise HTTPException(status_code=400, detail=f"Error updating company: {str(e)}")

api_app.include_router(api_debug_router)
