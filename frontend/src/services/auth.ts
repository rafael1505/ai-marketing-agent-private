import api from './api';
import axios from 'axios';
import { LoginResponse } from '@/types';

interface LoginCredentials {
  username: string;
  password: string;
}

export async function login(credentials: LoginCredentials): Promise<LoginResponse> {
  const formData = new URLSearchParams();
  formData.append('username', credentials.username);
  formData.append('password', credentials.password);

  console.log('API URL:', api.defaults.baseURL);
  console.log('Attempting login with credentials:', credentials.username);
    // Try multiple methods to get around proxy issues
  const loginMethods = [
    // Method 1: Use our own Next.js API route for authentication
    async () => {
      console.log('Trying login method 1: Next.js internal API route');
      // This route exists in our Next.js app at /api/auth/login
      const response = await axios.post('/api/auth/login', {
        username: credentials.username, 
        password: credentials.password
      }, {
        headers: {
          'Content-Type': 'application/json',
        },
      });
      return response;
    },
    // Method 2: Use the Next.js API route proxy
    async () => {
      console.log('Trying login method 2: Next.js API route proxy');
      // Use the Next.js rewrite rule we added to bypass proxy issues
      const response = await axios.post('/auth-proxy/login', formData, {
        headers: {
          'Content-Type': 'application/x-www-form-urlencoded',
        },
      });
      return response;
    },
    // Method 2: Direct API call with proxy disabled
    async () => {
      console.log('Trying login method 2: Direct API call with proxy disabled');
      const loginUrl = `${api.defaults.baseURL}/auth/login`;
      const response = await axios.post(loginUrl, formData, {
        headers: {
          'Content-Type': 'application/x-www-form-urlencoded',
        },
        proxy: false,
        timeout: 10000,
      });
      return response;
    },
    // Method 3: The original API instance
    async () => {
      console.log('Trying login method 3: Original API instance');
      const response = await api.post('/auth/login', formData, {
        headers: {
          'Content-Type': 'application/x-www-form-urlencoded',
        },
      });
      return response;
    }
  ];
  
  // Try each method in sequence
  let lastError = null;
  for (const method of loginMethods) {
    try {
      const response = await method();
      console.log('Login response:', response.status, response.data);
      return response.data;
    } catch (error: any) {
      console.error('Login attempt failed:', error.message);
      lastError = error;
      // Continue to next method
    }
  }
  
  // If all methods failed, throw the last error
  console.error('All login methods failed. Details of last error:');
  console.error('Error message:', lastError.message);
  if (lastError.response) {
    console.error('Response status:', lastError.response.status);
    console.error('Response data:', lastError.response.data);
  }
  throw lastError;
}

/**
 * Check if there is a stored authentication token
 * @returns True if a token is found in localStorage
 */
export function hasStoredToken(): boolean {
  if (typeof window === 'undefined') return false;
  
  const token = localStorage.getItem('token');
  return !!token;
}

/**
 * Check if the stored token is valid (not expired)
 * @returns True if token exists and is not expired
 */
export function hasValidToken(): boolean {
  if (typeof window === 'undefined') return false;
  
  try {
    const token = localStorage.getItem('token');
    if (!token) return false;
    
    // Parse the JWT to check expiration
    const tokenParts = token.split('.');
    if (tokenParts.length !== 3) return false;
    
    const payload = JSON.parse(atob(tokenParts[1]));
    const expiry = payload.exp * 1000; // Convert to milliseconds
    
    return Date.now() < expiry;
  } catch (e) {
    console.error('Error checking token validity:', e);
    return false;
  }
}

/**
 * Get the current authentication token
 * @returns The token string or null if not found
 */
export function getAuthToken(): string | null {
  if (typeof window === 'undefined') return null;
  return localStorage.getItem('token');
}
