# Authentication Developer Guide - AI Marketing Agent

This document provides guidance for developers working with authentication in the AI Marketing Agent application, particularly when handling FormData requests with file uploads.

## Authentication Dependencies

The application provides several authentication dependencies to choose from depending on your endpoint's needs:

### Standard JSON Authentication

For regular JSON API endpoints, use either:

```python
from app.api.v1.auth_fix import get_current_user_flexible, get_current_admin_user

@router.get("/my-endpoint")
async def my_endpoint(
    request: Request,
    current_user: dict = Depends(get_current_user_flexible)
):
    # Regular user authentication
    pass

@router.post("/admin-endpoint")
async def admin_endpoint(
    request: Request,
    current_user: dict = Depends(get_current_admin_user)
):
    # Admin user authentication
    pass
```

### FormData Authentication

For endpoints that handle FormData with file uploads, use the specialized FormData dependencies:

```python
from app.api.v1.auth_fix import get_current_user_formdata, get_admin_user_formdata

@router.put("/update-with-file")
async def update_with_file(
    request: Request,
    current_user: dict = Depends(get_current_user_formdata),
    file: UploadFile = File(...)
):
    # Regular user authentication with FormData
    pass

@router.put("/admin-update-with-file")
async def admin_update_with_file(
    request: Request,
    current_user: dict = Depends(get_admin_user_formdata),
    file: UploadFile = File(...)
):
    # Admin user authentication with FormData
    pass
```

## Handling Database IDs

When working with database entities, be aware that the application supports both ObjectId-based and string-based IDs:

```python
# For ObjectId-based entities
result = await collection.find_one({"_id": ObjectId(id)})

# For string-based entities (like test_company)
result = await collection.find_one({"_id": id})
```

The `CompanyDB` class includes enhanced methods for handling both types of IDs. When implementing new database classes, consider adding similar support:

```python
async def get_by_string_id(self, entity_id: str):
    """Get entity by string ID without converting to ObjectId"""
    return await self.collection.find_one({"_id": entity_id})
```

## Testing Authentication

### Development Tokens

For testing purposes, the authentication system recognizes development mock tokens:

```python
# A token with this format will be automatically accepted
token = "DEVELOPMENT_MOCK_TOKEN_FOR_TESTING_12345"
```

When a development token is detected, the system automatically creates a mock user with admin privileges.

### Test Scripts

Use these tools for testing authentication:

1. **Fast Verification**: `./verify_auth_complete.sh`
2. **Comprehensive Test**: `python3 test_auth_complete.py`
3. **Manual API Testing**: The `/api/v1/auth-test/auth-debug` endpoint

## Common Issues and Solutions

### 401 Unauthorized with FormData

If you encounter 401 Unauthorized errors with FormData requests:

1. Ensure you're using the appropriate FormData authentication dependency:
   - `get_current_user_formdata` or `get_admin_user_formdata`
   
2. Check that the client is correctly setting the Authorization header:
   ```javascript
   // Correct way to send FormData with auth
   const formData = new FormData();
   // Add form fields and files
   
   fetch('/api/endpoint', {
     method: 'POST',
     headers: {
       'Authorization': `Bearer ${token}`,
       // DO NOT set Content-Type for FormData requests!
     },
     body: formData
   });
   ```

### 404 Not Found Errors

If database operations result in 404 Not Found errors:

1. Check if you're using string IDs or ObjectIds:
   ```python
   # Log the ID type for debugging
   logger.info(f"ID type: {type(id)}, value: {id}")
   ```

2. Use the appropriate lookup method based on the ID type:
   - For general lookup: `get(id)`
   - For string-based IDs: `get_by_string_id(id)`

## Best Practices

1. **Always use the request parameter** in your endpoint functions to access the application context:
   ```python
   @router.post("/endpoint")
   async def endpoint(request: Request, ...):
       # Use request.app to access app-level resources
   ```

2. **Add detailed logging** for authentication processes:
   ```python
   logger.info(f"Authentication for user: {current_user.get('email')}")
   ```

3. **Handle edge cases** like missing fields in FormData:
   ```python
   # Make fields optional with defaults
   name: str = Form(...),
   description: str = Form(None),  # Optional field
   ```

4. **Always validate file uploads** before saving:
   ```python
   if file and file.filename:
       # Validate file type, size, etc.
       if file.content_type not in ALLOWED_TYPES:
           raise HTTPException(status_code=400, detail="Invalid file type")
   ```

By following these guidelines, you'll ensure that authentication works correctly across all types of requests in the AI Marketing Agent application.
