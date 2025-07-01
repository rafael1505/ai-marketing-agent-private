# AI Marketing Agent Authentication System Documentation

## Overview

This document explains the authentication system used in the AI Marketing Agent application, including how it works, common issues, and troubleshooting steps.

## Quick Fixes

### Use the Authentication Helper (NEW)

The easiest way to resolve authentication issues is to use the built-in Authentication Helper:

1. Make sure the frontend is running on port 3001
2. Open http://localhost:3001/auth-helper.html in your browser
3. Click the "Fix Authentication (Install Token)" button
4. After the token is installed, return to the application

### Generate a Fresh Token (NEW)

If your token has expired, you can generate a new one:

1. Open a terminal in the project root directory
2. Run the token generator script:
```bash
python generate_auth_token.py
```
3. Follow the instructions displayed in the terminal output

### Start with Correct Configuration (NEW)

For the best experience, use the complete startup script:
```bash
./start-complete.sh
```

## Authentication Flow

1. **Login Process**:
   - User submits credentials to `/api/v1/auth/login`
   - Backend validates credentials and returns a JWT token
   - Frontend stores the token in `localStorage`

2. **Request Authentication**:
   - Frontend retrieves token from `localStorage` 
   - Adds token to `Authorization: Bearer <token>` header for requests
   - Backend validates token and grants/denies access

3. **Form Data Submission**:
   - For regular JSON data: Content-Type set to `application/json`
   - For file uploads: FormData used without explicit Content-Type (browser handles boundary)
   - Auth token included in all requests regardless of content type

## API Endpoint Structure

```
http://127.0.0.1:8088/api/v1/           <- API Base URL
├── auth/                               <- Authentication endpoints
│   ├── login                           <- Login endpoint
│   ├── refresh                         <- Token refresh endpoint
│   └── test                            <- Authentication test endpoint
├── companies/                          <- Company endpoints
│   ├── active                          <- Get active company
│   └── :id                             <- Get/update specific company
└── ...
```

## Next.js API Proxy Configuration

The frontend uses several proxy configurations to handle API requests:

```javascript
// In next.config.js
{
  source: '/companies-proxy/:path*',     // Company API proxy
  destination: 'http://127.0.0.1:8088/api/v1/companies/:path*',
},
{
  source: '/direct-company-api/:id',     // Direct company API (no path mangling)
  destination: 'http://127.0.0.1:8088/api/v1/companies/:id',
},
```

## Common Authentication Issues

### 1. 401 Unauthorized Errors

**Possible causes:**
- Missing or invalid authentication token
- Token expiration
- Incorrect token format

**Solutions:**
- Check if token exists in localStorage
- Verify token format is correct
- Ensure token is properly included in request headers
- Try re-logging in to get a fresh token

### 2. 404 Not Found Errors with API Endpoints

**Possible causes:**
- Incorrect API endpoint path construction
- Duplicate path segments (e.g., `/companies/companies/id`)
- Proxy configuration issues

**Solutions:**
- Use proper relative path construction in API calls
- Use the direct-company-api proxy route for problematic endpoints
- Check Next.js proxy configuration

### 3. FormData Submission Issues

**Possible causes:**
- Manually setting Content-Type header for FormData requests
- Missing or incorrect authentication header with FormData

**Solutions:**
- Never set Content-Type manually for FormData requests
- Ensure the Authorization header is set correctly
- Use the proper FormData API correctly

## Code Examples

### Correct FormData Handling

```typescript
// Creating FormData for file upload
const formData = new FormData();
formData.append('name', 'Company Name');
formData.append('logo_file', fileObject);

// Making the request
const response = await fetch('/api/companies', {
  method: 'POST',
  headers: {
    'Authorization': `Bearer ${token}`,
    // DO NOT set Content-Type for FormData!
  },
  body: formData
});
```

### Correct Path Construction

```typescript
// Correct way to construct paths
const result = await makeReliableRequest<Company>(`/${id}`, {
  method: 'PUT',
  data: requestData,
  headers: authHeaders,
  proxyPath: 'companies-proxy',
});

// Alternative using direct-company-api 
const result = await makeReliableRequest<Company>(`${id}`, {
  method: 'PUT',
  data: requestData,
  headers: authHeaders,
  proxyPath: 'direct-company-api',
});
```

## Authentication Header Setup

```typescript
// Getting the token
const token = localStorage.getItem('token');

// Setting up auth headers
const authHeaders = token ? { 'Authorization': `Bearer ${token}` } : undefined;

// Adding headers to request
const response = await fetch(url, {
  method: 'GET',
  headers: {
    ...authHeaders,
    'Content-Type': 'application/json', // Only for JSON requests
  },
});
```

## Testing Authentication

### Browser-Based Testing

Visit http://localhost:3000/auth-test.html to:
- Check token presence
- Test API authentication
- Test company endpoints
- Test FormData submission

### Command-Line Testing

Run these scripts to diagnose authentication issues:

```bash
# General auth diagnostics
./diagnose_auth.sh

# Company API specific diagnostics
./diagnose_company_api.sh

# Interactive troubleshooter
./auth_troubleshooter.sh
```

## Development and Testing

For development and testing purposes, you can use a mock authentication token:

```javascript
// Generate a test token
const testToken = "DEVELOPMENT_MOCK_TOKEN_FOR_TESTING_" + Date.now();
localStorage.setItem('token', testToken);
```

## Debugging Authentication Issues

1. Check browser console for error messages
2. Examine network requests in browser devtools
3. Look for these common issues:
   - Missing Authorization header
   - Incorrect Content-Type header
   - Malformed API endpoint paths
   - CORS issues

4. Use the auth-test.html page to run targeted tests

## Version Information

This documentation applies to:
- Frontend version: 1.0.0+
- Backend API version: 1.0.0+
- Updated: May 2025
