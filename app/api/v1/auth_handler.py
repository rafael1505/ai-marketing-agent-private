from fastapi import APIRouter, Request, Depends, HTTPException, Header, File, Form, UploadFile
from typing import Dict, Any, Optional, Annotated

from app.api.v1.deps import get_current_user
from app.api.v1.auth_fix import get_current_user_flexible

router = APIRouter()

@router.get("/debug", response_model=Dict[str, Any])
async def auth_debug(
    request: Request,
    authorization: Optional[str] = Header(None)
) -> Dict[str, Any]:
    """Debug endpoint that shows information about the request's auth"""
    
    # Extract all headers
    headers = {key: value for key, value in request.headers.items()}
    
    # Try to parse the token
    token = None
    if authorization and authorization.lower().startswith("bearer "):
        token = authorization.split(" ")[1]
    
    return {
        "auth_header_present": authorization is not None,
        "auth_header": authorization[:20] + "..." if authorization else None,
        "token_extracted": token is not None,
        "token_preview": token[:10] + "..." if token else None,
        "all_headers": headers
    }

@router.post("/test-form", response_model=Dict[str, Any])
async def test_form_auth(
    request: Request,
    current_user: Annotated[dict, Depends(get_current_user_flexible)],
    test_field: str = Form(...),
    test_file: Optional[UploadFile] = File(None)
) -> Dict[str, Any]:
    """Test endpoint for FormData with authentication"""
    
    file_info = None
    if test_file:
        file_content = await test_file.read()
        file_info = {
            "filename": test_file.filename,
            "size": len(file_content),
            "content_type": test_file.content_type
        }
    
    return {
        "auth_success": True,
        "user": {
            "id": str(current_user.get("_id")),
            "email": current_user.get("email")
        },
        "received_data": {
            "test_field": test_field,
            "file": file_info
        }
    }

@router.post("/test-json", response_model=Dict[str, Any])
async def test_json_auth(
    request: Request,
    data: Dict[str, Any],
    current_user: Annotated[dict, Depends(get_current_user)]
) -> Dict[str, Any]:
    """Test endpoint for JSON with authentication"""
    
    return {
        "auth_success": True,
        "user": {
            "id": str(current_user.get("_id")),
            "email": current_user.get("email")
        },
        "received_data": data
    }
