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

@api_app.on_event("startup")
async def startup_db_client():
    """Initialize MongoDB connection on startup"""
    from app.db.mongodb import mongodb
    
    try:
        # Connect to MongoDB
        await mongodb.connect()
        api_app.mongodb = mongodb.db
        api_app.mongodb_client = mongodb.client
        logging.info("✅ Successfully connected to MongoDB - using real database")
        
        # Create indexes for optimal performance
        await mongodb.create_indexes()
        
        # Log collection counts
        users_count = await api_app.mongodb.users.count_documents({})
        companies_count = await api_app.mongodb.companies.count_documents({})
        providers_count = await api_app.mongodb.ai_providers.count_documents({})
        
        logging.info(f"📊 Database initialized: {users_count} users, {companies_count} companies, {providers_count} AI providers")
        
    except Exception as e:
        logging.error(f"❌ Failed to connect to MongoDB: {e}")
        logging.error("Please ensure MongoDB is running: systemctl start mongod")
        raise
    
    # Initialize i18n
    setup_i18n()

    # Log all registered routes for debugging
    def _log_routes(routes, prefix: str = ""):
        for route in routes:
            path = getattr(route, "path", None) or ""
            full_path = (prefix + path) if path != "/" else prefix or "/"
            if hasattr(route, "methods") and route.methods:
                logging.info(f"Route: {list(route.methods)} {full_path}")
            if hasattr(route, "routes"):
                _log_routes(route.routes, full_path)
    _log_routes(api_app.routes)
    logging.info("Registered routes listed above.")


@api_app.on_event("shutdown")
async def shutdown_db_client():
    """Close MongoDB connection on shutdown"""
    from app.db.mongodb import mongodb
    await mongodb.close()

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

# Add specific handler for Pydantic validation errors
from fastapi.exceptions import RequestValidationError
from pydantic import ValidationError

@api_app.exception_handler(RequestValidationError)
async def validation_exception_handler(request: Request, exc: RequestValidationError):
    """Handle FastAPI/Pydantic validation errors with detailed logging"""
    logging.error(f"[VALIDATION_ERROR] Path: {request.url.path}")
    logging.error(f"[VALIDATION_ERROR] Method: {request.method}")
    logging.error(f"[VALIDATION_ERROR] Body: {await request.body()}")
    logging.error(f"[VALIDATION_ERROR] Errors: {exc.errors()}")
    
    return JSONResponse(
        status_code=422,
        content={
            "success": False,
            "error": "Validation error",
            "error_details": {
                "error_type": "validation_error",
                "message": "Request validation failed",
                "user_message": "errors.validation.failed",
                "validation_errors": exc.errors(),
                "timestamp": datetime.now().isoformat()
            }
        }
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

# Alias for uvicorn (e.g. uvicorn app.main:app)
app = api_app
