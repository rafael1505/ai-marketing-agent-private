#!/bin/bash
#!/usr/bin/env bash

# Authentication System Fix Script
# This script applies all the necessary fixes for the authentication system

echo -e "\n=== Authentication System Fix Script ===\n"

# Stop any running API server or frontend
pkill -f "uvicorn app.main" || true
pkill -f "npm run dev" || true

# Function to display status
status() {
  if [ $1 -eq 0 ]; then
    echo -e "\033[0;32m✅ $2\033[0m"
  else
    echo -e "\033[0;31m❌ $2\033[0m"
    exit 1
  fi
}

# 1. Fix the auth endpoints - ensure consistency between frontend and backend
echo "Applying authentication endpoint fixes..."

# Ensure the auth.py router has both /login and /token endpoints
cat > /tmp/auth_router_fix.py << 'EOF'
from datetime import timedelta
from typing import Any, Annotated
from fastapi import APIRouter, Depends, HTTPException, status, Request
from fastapi.security import OAuth2PasswordRequestForm
from motor.motor_asyncio import AsyncIOMotorClient

from app.core.config import settings
from app.core.auth import create_access_token
from app.models.user import Token
from app.db.user import UserDB

router = APIRouter()

@router.post("/login", response_model=Token)
@router.post("/token", response_model=Token)  # Add compatibility endpoint
async def login(
    request: Request,
    form_data: Annotated[OAuth2PasswordRequestForm, Depends()]
) -> Any:
    user_db = UserDB(request.app.mongodb.users) # Corrected collection access
    user = await user_db.authenticate(form_data.username, form_data.password)
    
    if not user:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Incorrect email or password",
            headers={"WWW-Authenticate": "Bearer"},
        )
    elif not user.get("active", False):
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Inactive user"
        )
    
    access_token_expires = timedelta(minutes=settings.ACCESS_TOKEN_EXPIRE_MINUTES)
    access_token = create_access_token(
        data={"sub": str(user["_id"])},
        expires_delta=access_token_expires
    )
    
    return {
        "access_token": access_token,
        "token_type": "bearer"
    }

@router.get("/verify", response_model=dict)
async def verify_token(
    request: Request,
    current_user: dict = Depends(UserDB.get_current_user)
) -> Any:
    """
    Verify that the token is valid
    """
    return {
        "status": "ok",
        "user_id": str(current_user.get("_id")),
        "email": current_user.get("email")
    }
EOF

# Replace the auth.py file
cp /tmp/auth_router_fix.py "app/api/v1/auth.py"
status $? "Updated auth endpoints"

# 2. Fix the network utilities to handle FormData correctly
echo "Applying FormData fixes to network utilities..."

cat > /tmp/network_utils_fix.ts << 'EOF'
// Utility function to extract auth token consistently
export function getAuthToken(): string | null {
  if (typeof window === 'undefined') return null;
  
  // Try both localStorage and sessionStorage
  const token = localStorage.getItem('token') || sessionStorage.getItem('token');
  return token;
}

// Utility function to create proper auth headers
export function createAuthHeaders(): Record<string, string> {
  const token = getAuthToken();
  if (!token) return {};
  return { 'Authorization': `Bearer ${token}` };
}

// Utility function for handling FormData requests properly
export function setupFormDataRequest(
  data: FormData | any, 
  existingHeaders: Record<string, string> = {}
): { 
  data: any, 
  headers: Record<string, string> 
} {
  const headers = { ...existingHeaders, ...createAuthHeaders() };
  
  // If using FormData, ensure we don't set Content-Type (browser will handle it)
  if (data instanceof FormData) {
    // Explicitly delete Content-Type to let browser set it with proper boundary
    delete headers['Content-Type'];
    console.info('FormData detected: removed Content-Type header to let browser set it');
  } else {
    // For regular JSON requests, set the Content-Type
    headers['Content-Type'] = headers['Content-Type'] || 'application/json';
  }
  
  return { data, headers };
}
EOF

# Add the utilities file to frontend
mkdir -p "frontend/src/lib/auth"
cp /tmp/network_utils_fix.ts "frontend/src/lib/auth/auth-utils.ts"
status $? "Created auth utilities"

# 3. Add diagnostics for authentication issues
echo "Adding authentication diagnostics..."

cat > frontend/public/auth-diagnostics.html << 'EOF'
<!DOCTYPE html>
<html>
<head>
  <title>Authentication Diagnostics</title>
  <style>
    body { font-family: sans-serif; padding: 20px; max-width: 800px; margin: 0 auto; }
    .result { background: #f5f5f5; padding: 10px; border-radius: 4px; margin: 10px 0; }
    button { background: #4285f4; color: white; border: none; padding: 8px 16px; border-radius: 4px; margin: 5px; cursor: pointer; }
    button:hover { background: #3b78e7; }
    .error { color: red; }
    .success { color: green; }
    h2 { margin-top: 30px; border-bottom: 1px solid #eee; padding-bottom: 10px; }
  </style>
</head>
<body>
  <h1>Authentication Diagnostics</h1>
  
  <h2>1. Check Token</h2>
  <button id="checkToken">Check Auth Token</button>
  <div id="tokenResult" class="result"></div>
  
  <h2>2. Test Login</h2>
  <input id="username" placeholder="Username" value="test@example.com" />
  <input id="password" type="password" placeholder="Password" value="testpassword" />
  <button id="testLogin">Test Login</button>
  <div id="loginResult" class="result"></div>
  
  <h2>3. Test API with Auth</h2>
  <button id="testAPI">Test API with Auth</button>
  <div id="apiResult" class="result"></div>
  
  <h2>4. Test FormData with Auth</h2>
  <button id="testFormData">Test FormData with Auth</button>
  <div id="formDataResult" class="result"></div>
  
  <script>
    // Check Token
    document.getElementById('checkToken').addEventListener('click', function() {
      const token = localStorage.getItem('token');
      const result = document.getElementById('tokenResult');
      
      if (token) {
        result.innerHTML = `<div class="success">✅ Token found!</div>
          <div>Token: ${token.substring(0, 20)}...</div>
          <div>Length: ${token.length} characters</div>`;
      } else {
        result.innerHTML = '<div class="error">❌ No token found in localStorage</div>';
      }
    });
    
    // Test Login
    document.getElementById('testLogin').addEventListener('click', async function() {
      const username = document.getElementById('username').value;
      const password = document.getElementById('password').value;
      const result = document.getElementById('loginResult');
      
      result.innerHTML = 'Logging in...';
      
      const formData = new URLSearchParams();
      formData.append('username', username);
      formData.append('password', password);
      
      try {
        // Try both endpoints
        let response;
        
        try {
          response = await fetch('/api/v1/auth/login', {
            method: 'POST',
            headers: { 'Content-Type': 'application/x-www-form-urlencoded' },
            body: formData
          });
        } catch (e) {
          response = await fetch('/api/v1/auth/token', {
            method: 'POST',
            headers: { 'Content-Type': 'application/x-www-form-urlencoded' },
            body: formData
          });
        }
        
        if (response.ok) {
          const data = await response.json();
          localStorage.setItem('token', data.access_token);
          
          result.innerHTML = `<div class="success">✅ Login successful!</div>
            <div>Token: ${data.access_token.substring(0, 20)}...</div>
            <div>Token stored in localStorage</div>`;
        } else {
          const text = await response.text();
          result.innerHTML = `<div class="error">❌ Login failed (${response.status})</div>
            <div>${text}</div>`;
        }
      } catch (error) {
        result.innerHTML = `<div class="error">❌ Error: ${error.message}</div>`;
      }
    });
    
    // Test API with Auth
    document.getElementById('testAPI').addEventListener('click', async function() {
      const token = localStorage.getItem('token');
      const result = document.getElementById('apiResult');
      
      if (!token) {
        result.innerHTML = '<div class="error">❌ No token found. Please login first.</div>';
        return;
      }
      
      result.innerHTML = 'Testing API...';
      
      try {
        const response = await fetch('/api/v1/companies/active', {
          headers: { 'Authorization': `Bearer ${token}` }
        });
        
        if (response.ok) {
          const data = await response.json();
          result.innerHTML = `<div class="success">✅ API call successful!</div>
            <pre>${JSON.stringify(data, null, 2)}</pre>`;
        } else {
          const text = await response.text();
          result.innerHTML = `<div class="error">❌ API call failed (${response.status})</div>
            <div>${text}</div>`;
        }
      } catch (error) {
        result.innerHTML = `<div class="error">❌ Error: ${error.message}</div>`;
      }
    });
    
    // Test FormData with Auth
    document.getElementById('testFormData').addEventListener('click', async function() {
      const token = localStorage.getItem('token');
      const result = document.getElementById('formDataResult');
      
      if (!token) {
        result.innerHTML = '<div class="error">❌ No token found. Please login first.</div>';
        return;
      }
      
      result.innerHTML = 'Testing FormData...';
      
      // Create FormData
      const formData = new FormData();
      formData.append('name', 'Test Company');
      formData.append('description', 'This is a test from the diagnostic tool');
      
      // Create a simple text file as blob
      const fileContent = new Blob(['This is a test file'], { type: 'text/plain' });
      formData.append('logo_file', fileContent, 'test-file.txt');
      
      try {
        const response = await fetch('/api/v1/companies/test_company', {
          method: 'PUT',
          headers: { 'Authorization': `Bearer ${token}` },
          body: formData
        });
        
        if (response.ok) {
          const data = await response.json();
          result.innerHTML = `<div class="success">✅ FormData submission successful!</div>
            <pre>${JSON.stringify(data, null, 2)}</pre>`;
        } else {
          const text = await response.text();
          result.innerHTML = `<div class="error">❌ FormData submission failed (${response.status})</div>
            <div>${text}</div>`;
        }
      } catch (error) {
        result.innerHTML = `<div class="error">❌ Error: ${error.message}</div>`;
      }
    });
    
    // Initial check for token
    document.addEventListener('DOMContentLoaded', function() {
      document.getElementById('checkToken').click();
    });
  </script>
</body>
</html>
EOF

# Create a server-side authentication test handler
cat > "app/api/v1/auth_handler.py" << 'EOF'
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
EOF

# Update the API router to include the new auth_handler
sed -i '/api_router.include_router(auth.router, prefix="\/auth", tags=\["authentication"\])/a api_router.include_router(auth_handler.router, prefix="/auth-test", tags=["testing"])' "app/api/v1/api.py" || \
echo 'import app.api.v1.auth_handler as auth_handler
api_router.include_router(auth_handler.router, prefix="/auth-test", tags=["testing"])' >> "app/api/v1/api.py"

status $? "Added authentication diagnostics"

echo -e "\n✅ All authentication fixes have been applied!"
echo -e "Please restart both the API server and frontend to test the changes:"
echo -e "   1. API server: cd $(pwd) && uvicorn app.main:app --host 127.0.0.1 --port 8088"
echo -e "   2. Frontend: cd $(pwd)/frontend && npm run dev"
echo -e "\nThen visit http://localhost:3000/auth-diagnostics.html to test authentication."
