// Enhanced test endpoint to verify authentication handling with API
// Import NextResponse from the standard next/server path
import { NextRequest } from 'next/server';
import { NextResponse } from 'next/server';

// Helper function to log request details
function logRequestDetails(req: NextRequest, authHeader: string | null) {
  console.log(`Auth test request received: ${req.method} ${req.nextUrl.pathname}`);
  console.log(`Auth header: ${authHeader ? 'present' : 'missing'}`);
  if (authHeader) console.log(`Auth header value: ${authHeader.substring(0, 20)}...`);
  console.log(`Content-Type: ${req.headers.get('Content-Type')}`);
}

// GET request for basic authentication testing
export async function GET(request: NextRequest) {
  try {
    // Get auth token from request headers (if forwarded from browser)
    const authHeader = request.headers.get('Authorization');
    logRequestDetails(request, authHeader);
    
    // Get API server URL from environment
    const apiUrl = process.env.API_URL || 'http://127.0.0.1:8088';
    
    // Attempt to make an authenticated request to the API server
    const response = await fetch(`${apiUrl}/api/v1/companies/active`, {
      headers: {
        ...(authHeader ? { 'Authorization': authHeader } : {}),
        'Content-Type': 'application/json',
      }
    });
    
    if (!response.ok) {
      // If the API request failed, return the error details
      const errorText = await response.text();
      console.log(`API error: ${response.status} ${response.statusText}`);
      console.log(`API error details: ${errorText}`);
      
      return NextResponse.json({
        status: response.status,
        statusText: response.statusText,
        error: errorText,
        authHeader: authHeader ? 'present' : 'missing',
      }, { status: response.status });
    }
    
    const data = await response.json();
    console.log('API request successful');
    
    // Return success with the data and auth status
    return NextResponse.json({
      status: 'success',
      authHeader: authHeader ? 'present' : 'missing',
      data,
    });
  } catch (error: any) {
    console.error('Unexpected error in test-auth endpoint:', error);
    // Return any unexpected errors
    return NextResponse.json({
      status: 'error',
      message: error.message,
    }, { status: 500 });
  }
}

// POST request for testing FormData authentication 
export async function POST(request: NextRequest) {
  try {
    // Get auth token from request headers
    const authHeader = request.headers.get('Authorization');
    logRequestDetails(request, authHeader);
    
    const apiUrl = process.env.API_URL || 'http://127.0.0.1:8088';
    
    // Check request Content-Type
    const contentType = request.headers.get('Content-Type');
    console.log(`Request Content-Type: ${contentType}`);
    
    // Get request body based on content type
    let requestBody;
    let requestHeaders = {};
    
    if (contentType?.includes('multipart/form-data')) {
      // Handle FormData - clone and forward as is
      console.log('Handling FormData request');
      const formData = await request.formData();
      
      // Log FormData entries for debugging
      console.log('FormData entries:');
      for (const [key, value] of formData.entries()) {
        if (value instanceof File) {
          console.log(`- ${key}: [File ${value.name}, ${value.size} bytes]`);
        } else {
          console.log(`- ${key}: ${value}`);
        }
      }
      
      requestBody = formData;
      // Don't manually set Content-Type for FormData
    } else {
      // Handle JSON
      console.log('Handling JSON request');
      const jsonData = await request.json();
      requestBody = JSON.stringify(jsonData);
      requestHeaders = {
        'Content-Type': 'application/json',
      };
    }
    
    // Test against company API endpoint
    const response = await fetch(`${apiUrl}/api/v1/companies/test_company`, {
      method: 'PUT',
      headers: {
        ...(authHeader ? { 'Authorization': authHeader } : {}),
        ...requestHeaders,
      },
      body: requestBody,
    });
    
    const responseData = await response.json().catch(() => null) || await response.text();
    
    return NextResponse.json({
      status: response.status,
      statusText: response.statusText,
      authHeader: authHeader ? 'present' : 'missing',
      contentType: contentType,
      formDataTest: contentType?.includes('multipart/form-data'),
      data: responseData,
    });
  } catch (error: any) {
    console.error('Error in test-auth POST endpoint:', error);
    return NextResponse.json({
      status: 'error',
      message: error.message,
    }, { status: 500 });
  }
}
