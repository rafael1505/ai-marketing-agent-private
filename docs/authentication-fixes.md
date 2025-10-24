# Authentication Fixes for AI Marketing Agent

This document summarizes the changes made to fix authentication issues when submitting company information in the AI Marketing Agent application.

## Problems Fixed

1. **FormData Content-Type Header Issue**
   - Problem: When submitting multipart/form-data requests, the browser needs to set the Content-Type header with the proper boundary parameter automatically
   - Fix: Removed explicit Content-Type header for FormData requests in network-utils.ts

2. **API Endpoint Path Issue**
   - Problem: API requests were being sent to `/api/v1/companies/companies/test_company` (duplicated "companies")
   - Fix: Corrected path handling in updateCompany function to use the proper path format

3. **Enhanced Error Handling**
   - Improved error handling in company settings page to provide better feedback for authentication errors
   - Added specific error messages for different HTTP status codes (401, 403, 404)
   - Added detailed logging for debugging purposes

4. **Diagnostic Tools**
   - Created a test endpoint to verify authentication handling (/api/test-auth)
   - Created a diagnostic HTML page for testing authentication (auth-test.html)
   - Created a bash script for diagnosing authentication issues (diagnose_auth.sh)

## Files Modified

1. **/frontend/src/lib/network-utils.ts**
   - Removed automatic Content-Type header for FormData requests
   - Enhanced error logging and request debugging

2. **/frontend/src/services/companies.ts**
   - Fixed API path construction
   - Removed Content-Type header for FormData requests
   - Added detailed logging for debugging

3. **/frontend/src/app/[locale]/settings/page.tsx**
   - Improved error handling with specific messages for different types of errors
   - Enhanced authentication error detection and reporting

4. **/frontend/next.config.js**
   - Added an additional debug route for API diagnostics

## New Files Created

1. **/frontend/src/app/api/test-auth/route.ts**
   - Test endpoint to verify authentication handling

2. **/frontend/public/auth-test.html**
   - Diagnostic page for testing authentication in the browser

3. **/diagnose_auth.sh**
   - Bash script for diagnosing authentication issues

## How to Verify the Fixes

1. Run the API and frontend servers:
   ```bash
   # Run API server with mock database
   npm run api-dev
   
   # Run frontend development server
   cd frontend && npm run dev
   ```

2. Run the diagnostic script:
   ```bash
   ./diagnose_auth.sh
   ```

3. Visit the diagnostic page in the browser:
   ```
   http://localhost:3000/auth-test.html
   ```

4. Test company settings page:
   ```
   http://localhost:3000/en/settings
   ```

## Technical Details

### FormData and Content-Type Headers

When submitting multipart/form-data requests with files, the browser needs to automatically generate a Content-Type header with a boundary parameter that separates the different parts of the form data. If we set the Content-Type header manually to 'multipart/form-data' without a boundary, the request will fail.

Before:
```javascript
requestHeaders = {
  ...headers,
  ...authHeaders,
  'Content-Type': contentTypeHeader  // This would override the browser's header
};
```

After:
```javascript
// Only add Content-Type if it's not a FormData request
if (!(data instanceof FormData)) {
  requestHeaders['Content-Type'] = contentTypeHeader;
}
```

### Multiple API Endpoint Attempts

To make the API requests more resilient, we implemented a fallback mechanism that tries multiple endpoints:

```typescript
// First attempt with companies-proxy
try {
  const result = await makeReliableRequest<Company>(`/${id}`, {
    method: 'PUT',
    data: requestData,
    headers: authHeaders,
    proxyPath: 'companies-proxy',
  });
  
  return result;
} catch (error1) {
  // Second attempt with direct-company-api
  const result2 = await makeReliableRequest<Company>(`${id}`, {
    method: 'PUT',
    data: requestData,
    headers: authHeaders,
    proxyPath: 'direct-company-api',
  });
  
  return result2;
}
```

### Company API Test Function

The auth-test.html page now includes a comprehensive API test function to verify company endpoints:

```javascript
async function testCompanyApi() {
  // Tests multiple endpoints:
  // 1. Next.js Proxy (/companies-proxy/test_company)
  // 2. Direct Company API (/direct-company-api/test_company)
  // 3. Active Company (/companies-proxy/active)
  // 4. FormData submission test
  
  // For each endpoint, it displays the response and status
}
```

This allows us to quickly diagnose issues with different endpoint configurations and authentication methods.

### Authentication Token Handling

We now ensure the authentication token is properly added to all requests, including FormData requests:

```javascript
const token = typeof window !== 'undefined' ? localStorage.getItem('token') : null;
const authHeaders = token ? { 'Authorization': `Bearer ${token}` } : {};
```

By applying these fixes, the application should now successfully authenticate and submit company data, including file uploads.
