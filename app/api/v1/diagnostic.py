from fastapi import APIRouter, Request, Response
from app.db.user import UserDB
import logging
from fastapi.routing import APIRoute
import json

router = APIRouter()

@router.get("/ping")
async def ping():
    """Simple endpoint to verify API accessibility"""
    return {"status": "ok", "message": "API is operational"}

@router.get("/health")
async def health():
    """Health check endpoint"""
    return {"status": "ok", "message": "Service is healthy"}

@router.get("/debug-db")
async def debug_db(request: Request):
    """Checks if the database connection is working properly"""
    try:
        # Get the mongodb object from the request
        mongodb = request.app.mongodb
        
        # Try to access the users collection
        if hasattr(mongodb, 'users'):
            # For SimpleMockDatabase which exposes collections as properties
            user_db = UserDB(mongodb.users)
            # Count users to verify it's working
            user_count = await mongodb.users.count_documents({})
        else:
            # For real MongoDB which uses dictionary-like access
            from app.core.config import settings
            user_db = UserDB(mongodb[settings.MONGODB_DB].users)
            user_count = await mongodb[settings.MONGODB_DB].users.count_documents({})
        
        return {
            "status": "ok", 
            "database": "connected",
            "user_count": user_count,
        }
    except Exception as e:
        logging.exception("Database diagnostic check failed")
        return {
            "status": "error",
            "error": str(e),
            "error_type": type(e).__name__
        }
        
@router.get("/endpoints")
async def list_endpoints(request: Request):
    """List all available API endpoints"""
    app = request.app
    
    # Get all routes
    routes = []
    
    # Process FastAPI routes
    for route in app.routes:
        if isinstance(route, APIRoute):
            routes.append({
                "path": route.path,
                "name": route.name,
                "methods": route.methods,
                "tags": getattr(route, "tags", [])
            })
    
    # Group by prefix
    grouped_routes = {}
    for route in routes:
        path_parts = route["path"].split("/")
        if len(path_parts) > 2:
            prefix = f"/{path_parts[1]}"
            if prefix not in grouped_routes:
                grouped_routes[prefix] = []
            grouped_routes[prefix].append(route)
    
    return {
        "status": "ok",
        "total_routes": len(routes),
        "endpoints_by_prefix": grouped_routes
    }
