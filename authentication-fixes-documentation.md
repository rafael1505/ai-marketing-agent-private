# Authentication System Fixes and Documentation

## Overview of Authentication Issues Fixed

This document explains the fixes applied to resolve the authentication issues with FormData submissions in the AI Marketing Agent application.

### Key Issues Addressed

1. **401 Unauthorized errors** when submitting forms with file uploads
2. **404 Not Found errors** due to incorrect API path construction
3. **Authentication token handling** with FormData requests

## Backend Fixes

### Custom Authentication Dependency

We've created a custom authentication dependency that handles both regular JSON requests and FormData/multipart requests:

```python
# app/api/v1/auth_fix.py
async def get_token_from_request(request: Request) -> Optional[str]:
    """
    Extract token from request headers regardless of content type
    Works for both JSON and multipart/form-data requests
    """
    authorization: str = request.headers.get("Authorization", "")
    scheme, token = get_authorization_scheme_param(authorization)
    
    if not authorization or scheme.lower() != "bearer":
        return None
    return token

# Combined dependency that works with all request types
async def get_current_user_flexible(
    request: Request,
    token: str = Depends(oauth2_scheme),
) -> Dict[str, Any]:
    # Fallback to manual token extraction if oauth2_scheme fails
    # This handles multipart/form-data requests properly
```

### Updated Company API Endpoint

The PUT endpoint for company updates now uses this flexible authentication:

```python
@router.put("/{company_id}", response_model=CompanyInDB)
async def update_company(
    company_id: str,
    request: Request,
    current_user: Annotated[dict, Depends(get_admin_user_fixed)],  # Uses the fixed auth
    # ... other parameters
)
```

### Diagnostic Endpoints

Added special diagnostic endpoints for testing authentication:

```
/api/v1/auth-test/test-form - Test FormData authentication
/api/v1/auth-test/test-json - Test JSON authentication 
/api/v1/auth-test/auth-debug - Debug authentication headers
```

## Frontend Fixes

### FormData Handling in network-utils.ts

Updated the network utility to handle FormData requests correctly:

```typescript
// For FormData requests, explicitly delete Content-Type header to let the browser set it
if (data instanceof FormData) {
  delete requestHeaders['Content-Type'];
  console.log('FormData detected: removed Content-Type header to let browser set it');
}
```

### Token Extraction and Storage

Improved token handling in the network utilities:

```typescript
// Try both localStorage and sessionStorage
const token = typeof window !== 'undefined' ? 
  (localStorage.getItem('token') || sessionStorage.getItem('token')) : null;

// Always normalize the auth header format with Bearer prefix  
const authHeaders = token ? { 'Authorization': `Bearer ${token}` } : {};
```

### Better Error Handling in Settings Page

Enhanced error messages and debugging for authentication failures:

```typescript
console.group("🔐 Authentication Debug Info");
console.log("Token exists:", !!token);
console.log("Token preview:", token ? `${token.substring(0, 15)}...` : 'none');
console.log("Token length:", token ? token.length : 0);
// Additional debug info...
```

## Debugging Tools

1. **Authentication Debug Suite** - A comprehensive browser-based tool for testing authentication:
   - Available at `/auth-debug-suite.html`
   - Tests token storage, validation, API endpoints, and FormData submissions

2. **Direct API Test Script** - Python script for testing authentication directly:
   - `auth_api_test.py` - Tests login, token validation, and FormData uploads

## Root Causes and Fixes

1. **Content-Type Header Issue** 
   - **Problem**: Setting Content-Type for FormData requests breaks the automatic boundary setting
   - **Fix**: Explicitly remove Content-Type header for FormData requests

2. **Token Authorization Format**
   - **Problem**: Inconsistent "Bearer" prefix in Authorization headers
   - **Fix**: Always normalize to `Authorization: Bearer <token>`

3. **FastAPI OAuth2 Dependency Limitation**
   - **Problem**: Standard OAuth2PasswordBearer doesn't work well with multipart/form-data
   - **Fix**: Custom authentication dependency that handles all request types

4. **API Path Construction**
   - **Problem**: Inconsistent paths leading to 404 errors
   - **Fix**: Standardized API path construction in frontend services

## Testing the Fixes

1. Use the Authentication Debug Suite to test all authentication scenarios
2. Check that file uploads work correctly on the Settings page
3. Verify that token authentication works for both JSON and FormData requests

## Next Steps for System Improvement

1. **Token Refresh Mechanism** - Implement token refresh to prevent session expiration
2. **Consistent Error Handling** - Standardize authentication error responses
3. **Logging Enhancement** - Add structured logging for authentication events
4. **Authentication Metrics** - Track success/failure rates to detect issues

## Conclusion

The authentication system now properly handles both JSON and FormData requests. The fixes preserve the proper Content-Type handling required by multipart form submissions while ensuring that authentication tokens are correctly applied to all requests.
