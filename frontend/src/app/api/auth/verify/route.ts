// Import NextResponse from the standard next/server path
import { NextRequest } from 'next/server';
import { NextResponse } from 'next/server';

// GET handler for token verification
export async function GET(request: NextRequest) {
  try {
    // Get the Authorization header
    const authHeader = request.headers.get('Authorization');
    
    if (!authHeader || !authHeader.startsWith('Bearer ')) {
      return NextResponse.json({ 
        detail: "Authorization header missing or invalid" 
      }, { status: 401 });
    }

    const token = authHeader.substring(7); // Remove 'Bearer ' prefix

    // Make server-side request to backend API (bypasses corporate proxy)
    const backendUrl = process.env.API_URL || 'http://127.0.0.1:8088';
    
    console.log('Verifying token with backend:', `${backendUrl}/api/v1/auth/verify`);
    
    const response = await fetch(`${backendUrl}/api/v1/auth/verify`, {
      method: 'GET',
      headers: {
        'Authorization': `Bearer ${token}`,
        'Content-Type': 'application/json',
      },
      // Important: Set no proxy environment variables for server-side requests
    });

    console.log('Backend verification response:', response.status);

    if (response.ok) {
      const userData = await response.json();
      return NextResponse.json(userData, { status: 200 });
    } else {
      const error = await response.text();
      console.error('Backend verification failed:', error);
      return NextResponse.json({ 
        detail: "Token verification failed" 
      }, { status: response.status });
    }
  } catch (error) {
    console.error('Error in verify API route:', error);
    return NextResponse.json({ 
      detail: "Internal server error during token verification" 
    }, { status: 500 });
  }
}
