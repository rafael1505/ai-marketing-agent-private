#!/usr/bin/env python3
"""
Custom auth dependency implementation that works with both JSON and FormData requests
This file can be used to replace the standard FastAPI auth dependency
"""

from typing import Optional, Annotated, Dict, Any
from fastapi import Depends, HTTPException, status, Request
from fastapi.security import OAuth2PasswordBearer
from fastapi.security.utils import get_authorization_scheme_param
from jose import jwt
from app.core.auth import verify_token
from app.core.config import settings
from app.db.user import UserDB
from motor.motor_asyncio import AsyncIOMotorClient
import logging

# Set up logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

# Standard OAuth2 scheme for regular requests
oauth2_scheme = OAuth2PasswordBearer(tokenUrl=f"{settings.API_V1_STR}/auth/token")

# Custom token extractor that works with all request types
async def get_token_from_request(request: Request) -> Optional[str]:
    """
    Extract token from request headers regardless of content type
    Works for both JSON and multipart/form-data requests
    """
    # Get authorization header
    authorization: str = request.headers.get("Authorization", "")
    
    # Log the headers for debugging
    logger.info(f"Request headers: {request.headers}")
    logger.info(f"Content-Type: {request.headers.get('content-type', 'Not specified')}")
    
    # Extract token using FastAPI's utility
    scheme, token = get_authorization_scheme_param(authorization)
    
    # Debug logging
    if token:
        logger.info(f"Token found with scheme: {scheme}")
        logger.debug(f"Token preview: {token[:15]}...")
    else:
        logger.warning("No authorization token found in request")
        
        # If no Authorization header, try looking for it in other headers (e.g., lowercase)
        for header, value in request.headers.items():
            if header.lower() == "authorization":
                logger.info(f"Found authorization in alternate header: {header}")
                alt_scheme, alt_token = get_authorization_scheme_param(value)
                if alt_token:
                    logger.info(f"Using token from alternate header with scheme: {alt_scheme}")
                    return alt_token
    
    # Validate proper authorization format
    if not authorization or scheme.lower() != "bearer":
        return None
        
    return token

# Combined dependency that works with all request types
async def get_current_user_flexible(
    request: Request,
    token: str = None,  # Make token optional to handle FormData requests
) -> Dict[str, Any]:
    """
    Get the current user from the token in the request headers
    Works with both regular and multipart/form-data requests
    """
    credentials_exception = HTTPException(
        status_code=status.HTTP_401_UNAUTHORIZED,
        detail="Could not validate credentials",
        headers={"WWW-Authenticate": "Bearer"},
    )
    
    # First try to get token from the request headers directly
    if not token:
        token = await get_token_from_request(request)
        if not token:
            logger.error("Authentication failed: No token found in request headers")
            raise credentials_exception
    
    # Verify the token
    payload = verify_token(token)
    if payload is None:
        logger.error("Authentication failed: Invalid token")
        raise credentials_exception
    
    # Extract user ID from token
    user_id: str = payload.get("sub")
    if user_id is None:
        logger.error("Authentication failed: No user ID in token")
        raise credentials_exception
    
    # Special case for development mock tokens and test environment
    if (token and 'DEVELOPMENT_MOCK_TOKEN' in token) or user_id == '1':
        logger.info(f"Using development mock user for token")
        return {
            "_id": "1",
            "id": "1",
            "email": "test@example.com",
            "name": "Test User",
            "active": True,
            "is_admin": True
        }
        
    # For real authentication, continue with database lookup
    # Access the mongodb object from the request
    mongodb = request.app.mongodb
    
    # Access users collection
    if hasattr(mongodb, 'users'):
        # For SimpleMockDatabase which exposes collections as properties
        user_db = UserDB(mongodb.users)
    else:
        # For real MongoDB which uses dictionary-like access
        user_db = UserDB(mongodb[settings.MONGODB_DB].users)
        
    # Get user from database
    user = await user_db.get(user_id)
    
    if user is None:
        logger.error(f"Authentication failed: User {user_id} not found")
        raise credentials_exception
        
    logger.info(f"Authentication successful for user: {user_id}")
    return user

# Redefine dependencies using the flexible authentication
async def get_current_active_user(
    request: Request,
    current_user: dict = Depends(get_current_user_flexible)
) -> dict:
    if not current_user.get("active", False):
        raise HTTPException(status_code=400, detail="Inactive user")
    return current_user

async def get_current_admin_user(
    request: Request,
    current_user: dict = Depends(get_current_active_user)
) -> dict:
    if not current_user.get("is_admin", False):
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="The user doesn't have enough privileges"
        )
    return current_user

# Special dependency for FormData requests that doesn't use OAuth2PasswordBearer
async def get_current_user_formdata(request: Request) -> Dict[str, Any]:
    """
    Special dependency for FormData requests that extracts the token manually
    Use this for endpoints that accept FormData with file uploads
    """
    credentials_exception = HTTPException(
        status_code=status.HTTP_401_UNAUTHORIZED,
        detail="Could not validate credentials",
        headers={"WWW-Authenticate": "Bearer"},
    )
    
    # Log all headers for debugging
    logger.info(f"FormData Auth - All request headers: {request.headers}")
    
    # Extract token directly from the Authorization header
    authorization: str = request.headers.get("Authorization", "")
    logger.info(f"FormData Auth - Authorization header: {authorization}")
    
    # Extract token using FastAPI's utility
    scheme, token = get_authorization_scheme_param(authorization)
    logger.info(f"FormData Auth - Scheme: {scheme}, Token: {token[:20]}...")
    
    if not token:
        logger.error("FormData Authentication failed: No token found in request headers")
        raise credentials_exception
    
    # Verify the token
    payload = verify_token(token)
    if payload is None:
        logger.error("FormData Authentication failed: Invalid token")
        raise credentials_exception
    
    # Extract user ID from token
    user_id: str = payload.get("sub")
    if user_id is None:
        logger.error("FormData Authentication failed: No user ID in token")
        raise credentials_exception
    
    # Special case for development mock tokens and test environment - check before DB access
    if (token and 'DEVELOPMENT_MOCK_TOKEN' in token) or user_id == '1':
        logger.info(f"Using development mock user for FormData token")
        return {
            "_id": "1",
            "id": "1",
            "email": "test@example.com",
            "name": "Test User",
            "active": True,
            "is_admin": True
        }

    # For real authentication, continue with database lookup
    # Access the mongodb object from the request
    mongodb = request.app.mongodb
    # Access users collection
    if hasattr(mongodb, 'users'):
        # For SimpleMockDatabase which exposes collections as properties
        user_db = UserDB(mongodb.users)
    else:
        # For real MongoDB which uses dictionary-like access
        user_db = UserDB(mongodb[settings.MONGODB_DB].users)
        
    # Get user from database
    user = await user_db.get(user_id)
    
    if user is None:
        logger.error(f"FormData Authentication failed: User {user_id} not found")
        raise credentials_exception
        
    logger.info(f"FormData Authentication successful for user: {user_id}")
    return user

# Convenience dependency for FormData admin authentication
async def get_admin_user_formdata(request: Request) -> Dict[str, Any]:
    """
    Special dependency for FormData requests that require admin privileges
    """
    user = await get_current_user_formdata(request)
    
    if not user.get("active", False):
        raise HTTPException(status_code=400, detail="Inactive user")
        
    if not user.get("is_admin", False):
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="The user doesn't have enough privileges"
        )
        
    return user
