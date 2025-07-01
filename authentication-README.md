# AI Marketing Agent: Authentication System

## Overview

This README focuses on the authentication system for the AI Marketing Agent application. It provides guidance on how authentication works, how to troubleshoot common issues, and how to verify that all fixes have been implemented correctly.

## Table of Contents

1. [Authentication System Components](#authentication-system-components)
2. [Common Issues Fixed](#common-issues-fixed)
3. [Documentation](#documentation)
4. [Diagnostic Tools](#diagnostic-tools)
5. [Testing and Verification](#testing-and-verification)
6. [Troubleshooting](#troubleshooting)

## Authentication System Components

The authentication system consists of the following components:

* **Backend API (FastAPI)**
  * Authentication endpoints (`/api/v1/auth/*`)
  * JWT token generation and validation
  * Protected company endpoints (`/api/v1/companies/*`)

* **Frontend (Next.js)**
  * Token management in localStorage
  * Request authentication with HTTP headers
  * FormData handling for file uploads
  * API proxy configuration

## Common Issues Fixed

We've addressed several authentication issues in the system:

1. **Duplicate API Path Segments**
   * Problem: Requests were being sent to `/api/v1/companies/companies/id`
   * Solution: Fixed path construction in `companies.ts` to avoid duplication

2. **FormData Content-Type Issues**
   * Problem: Explicitly setting Content-Type header for FormData requests broke file uploads
   * Solution: Removed Content-Type header setting for FormData in `network-utils.ts`

3. **Authentication Token Handling**
   * Problem: Inconsistent auth token inclusion in requests
   * Solution: Ensured explicit inclusion of auth token in all company API requests

4. **API Proxy Configuration**
   * Problem: Next.js API routes weren't correctly forwarding requests
   * Solution: Added direct company API proxy route in `next.config.js`

## Documentation

We've created comprehensive documentation for the authentication system:

* **[authentication-guide.md](./authentication-guide.md)**: Comprehensive guide to the authentication system
* **[authentication-fixes.md](./authentication-fixes.md)**: Detailed explanation of fixes implemented
* **[auth-fixes-summary.md](./auth-fixes-summary.md)**: Concise summary of all fixes

## Diagnostic Tools

Several diagnostic tools have been developed to help troubleshoot authentication issues:

* **[auth-test.html](./frontend/public/auth-test.html)**: Browser-based authentication testing tool
  * Visit at http://localhost:3000/auth-test.html when servers are running
  * Tests auth token management, API endpoints, and FormData uploads

* **[diagnose_auth.sh](./diagnose_auth.sh)**: Command-line diagnostics for authentication issues
  * Run with `./diagnose_auth.sh` to check basic authentication functionality

* **[diagnose_company_api.sh](./diagnose_company_api.sh)**: Command-line diagnostics for company API issues
  * Run with `./diagnose_company_api.sh` to test company endpoints specifically

* **[auth_troubleshooter.sh](./auth_troubleshooter.sh)**: Interactive troubleshooting script
  * Run with `./auth_troubleshooter.sh` for guided diagnosis and fixing

## Testing and Verification

To verify that all authentication fixes are working correctly:

1. **Start the servers**:
   ```bash
   # Start API server
   cd /path/to/project
   uvicorn app.main:app --host 127.0.0.1 --port 8088 --reload
   
   # Start frontend
   cd frontend
   npm run dev
   ```

2. **Run the verification script**:
   ```bash
   ./verify_authentication_fixes.sh
   ```
   This script runs a comprehensive test suite and reports results.

3. **Check the browser-based test page**:
   Visit http://localhost:3000/auth-test.html and run the tests.

## Troubleshooting

If you encounter authentication issues:

1. **Check the browser console** for specific error messages.

2. **Inspect network requests** in browser devtools:
   * Verify Authorization header is present
   * Check for correct Content-Type headers
   * Look for proper API endpoint paths

3. **Run the troubleshooter**:
   ```bash
   ./auth_troubleshooter.sh
   ```
   
4. **Common error codes**:
   * **401 Unauthorized**: Authentication token missing or invalid
   * **404 Not Found**: Incorrect API path or proxy configuration
   * **422 Unprocessable Entity**: FormData or request body issues

5. **Clear browser storage**:
   * Open browser devtools
   * Go to Application > Storage > Local Storage
   * Clear the token and try logging in again

## Development and Testing

For development and testing, you can use a mock token:

```javascript
// In browser console
localStorage.setItem('token', 'DEVELOPMENT_MOCK_TOKEN_FOR_TESTING');
```

## License

This project is licensed under [LICENSE INFORMATION].
