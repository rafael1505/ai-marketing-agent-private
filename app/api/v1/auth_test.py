"""
FormData authentication test endpoint for troubleshooting
"""
from typing import Any, Annotated, List, Dict
from fastapi import APIRouter, Depends, Request, File, UploadFile, Form, Header
import logging
from app.api.v1.deps import get_current_admin_user
from app.api.v1.auth_fix import (
    get_current_user_flexible,
    get_current_admin_user as get_admin_user_fixed,
    get_current_user_formdata,
    get_admin_user_formdata
)

# Configure logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

router = APIRouter()

@router.post("/test-form", response_model=Dict[str, Any])
async def test_form_authentication(
    request: Request,
    current_user: Annotated[dict, Depends(get_admin_user_fixed)], 
    test_field: str = Form("default"),
    test_file: UploadFile = File(None),
    content_type: str = Header(None)
) -> Any:
    """
    Test endpoint for FormData authentication
    """
    logger.info(f"FormData auth test received, content-type: {content_type}")
    logger.info(f"Authenticated user: {current_user.get('email', 'unknown')}")
    
    result = {
        "status": "success",
        "message": "FormData authentication working correctly",
        "user": current_user.get("email"),
        "test_field": test_field,
        "file_received": test_file is not None,
    }
    
    if test_file:
        result["file_info"] = {
            "filename": test_file.filename,
            "content_type": test_file.content_type,
            "size": len(await test_file.read()),
        }
        # Reset file position after reading
        await test_file.seek(0)
    
    return result

@router.post("/test-json", response_model=Dict[str, Any])
async def test_json_authentication(
    request: Request,
    current_user: dict = Depends(get_admin_user_fixed),
    data: Dict[str, Any] = None
) -> Any:
    """
    Test endpoint for JSON authentication
    """
    logger.info(f"JSON auth test received")
    logger.info(f"Authenticated user: {current_user.get('email', 'unknown')}")
    
    if data is None:
        data = {}
    
    return {
        "status": "success",
        "message": "JSON authentication working correctly",
        "user": current_user.get("email"),
        "received_data": data,
    }

@router.get("/auth-debug", response_model=Dict[str, Any])
async def auth_debug_info(
    request: Request,
    authorization: str = Header(None),
    content_type: str = Header(None),
) -> Any:
    """
    Debug endpoint to check authentication headers
    """
    headers = {key: value for key, value in request.headers.items()}
    
    # Try to extract token from header
    token = None
    if authorization and authorization.lower().startswith("bearer "):
        token = authorization.split(" ")[1]
    
    return {
        "status": "info",
        "has_auth_header": authorization is not None,
        "auth_header_format": "Bearer" if authorization and authorization.lower().startswith("bearer ") else "Unknown/None",
        "token_length": len(token) if token else 0,
        "content_type": content_type,
        "all_headers": headers,
    }

@router.post("/test-form-direct", response_model=Dict[str, Any])
async def test_form_authentication_direct(
    request: Request,
    test_field: str = Form("default"),
    test_file: UploadFile = File(None),
    content_type: str = Header(None)
) -> Any:
    """
    Direct test endpoint for FormData authentication without dependency injection
    """
    # Manual token extraction from request
    authorization = request.headers.get("Authorization", "")
    logger.info(f"Authorization header: {authorization}")
    
    # Log all headers for debugging
    logger.info(f"All headers: {request.headers}")
    logger.info(f"Content-Type: {content_type}")
    
    # Extract token manually
    token = None
    if authorization and authorization.lower().startswith("bearer "):
        token = authorization.split(" ")[1]
        logger.info(f"Token extracted: {token[:15]}...")
    
    result = {
        "status": "success",
        "message": "FormData direct test",
        "test_field": test_field,
        "file_received": test_file is not None,
        "auth_header_present": authorization != "",
        "token_extracted": token is not None,
    }
    
    if test_file:
        result["file_info"] = {
            "filename": test_file.filename,
            "content_type": test_file.content_type,
            "size": len(await test_file.read()),
        }
        # Reset file position after reading
        await test_file.seek(0)
    
    return result

@router.post("/test-form-special", response_model=Dict[str, Any])
async def test_form_authentication_special(
    request: Request,
    current_user: dict = Depends(get_current_user_formdata),
    test_field: str = Form("default"),
    test_file: UploadFile = File(None),
    content_type: str = Header(None)
) -> Any:
    """
    Test endpoint using our special FormData authentication dependency
    """
    logger.info(f"FormData auth test with special dependency, content-type: {content_type}")
    logger.info(f"Authenticated user: {current_user.get('email', 'unknown')}")
    
    result = {
        "status": "success",
        "message": "FormData authentication with special dependency working correctly",
        "user": current_user.get("email"),
        "test_field": test_field,
        "file_received": test_file is not None,
    }
    
    if test_file:
        result["file_info"] = {
            "filename": test_file.filename,
            "content_type": test_file.content_type,
            "size": len(await test_file.read()),
        }
        # Reset file position after reading
        await test_file.seek(0)
    
    return result
