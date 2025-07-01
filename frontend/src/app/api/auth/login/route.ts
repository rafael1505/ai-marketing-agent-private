// Import NextResponse from the standard next/server path
import { NextRequest } from 'next/server';
import { NextResponse } from 'next/server';

// POST handler for App Router API routes
export async function POST(request: NextRequest) {
  try {
    // Parse the request body as JSON
    const body = await request.json();
    const { username, password } = body;

    console.log('Login API route called with username:', username);

    // Make server-side request to backend API (bypasses corporate proxy)
    const backendUrl = process.env.API_URL || 'http://127.0.0.1:8088';
    
    // Create form data for backend API
    const formData = new URLSearchParams();
    formData.append('username', username);
    formData.append('password', password);

    console.log('Attempting backend login:', `${backendUrl}/api/v1/auth/token`);

    const response = await fetch(`${backendUrl}/api/v1/auth/token`, {
      method: 'POST',
      headers: {
        'Content-Type': 'application/x-www-form-urlencoded',
      },
      body: formData.toString(),
    });

    console.log('Backend login response:', response.status);

    if (response.ok) {
      const tokenData = await response.json();
      return NextResponse.json(tokenData, { status: 200 });
    } else {
      const error = await response.text();
      console.error('Backend login failed:', error);
      return NextResponse.json({ 
        detail: "Incorrect email or password" 
      }, { status: 401 });
    }
  } catch (error) {
    console.error('Error in login API route:', error);
    return NextResponse.json({ error: 'Internal Server Error' }, { status: 500 });
  }
}
