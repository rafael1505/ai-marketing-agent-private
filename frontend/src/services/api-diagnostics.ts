import api from './api';
import axios from 'axios';
import { APIStatus, ConnectionInfo } from '@/types';

/**
 * Tests the API connection and returns status information
 * This is useful for showing API status in the UI
 */
export async function checkAPIConnection(): Promise<ConnectionInfo> {
  const connectionInfo: ConnectionInfo = {
    isOnline: typeof navigator !== 'undefined' && navigator.onLine,
    apiAccessible: false,
    apiConnected: false,
    apiPort: null,
    authWorking: false,
    lastChecked: new Date(),
    error: null,
  };
  
  if (!connectionInfo.isOnline) {
    connectionInfo.error = 'Browser is offline. Please check your internet connection.';
    return connectionInfo;
  }
  
  try {
    // First, try direct connection to port 8088
    try {
      const response = await axios.get('http://127.0.0.1:8088/api/v1/diagnostic/ping', {
        proxy: false,
        timeout: 2000,
        headers: {
          'Cache-Control': 'no-cache',
          'Pragma': 'no-cache'
        }
      });
      
      if (response.status === 200) {
        connectionInfo.apiAccessible = true;
        connectionInfo.apiPort = 8088;
        console.log('API accessible directly on port 8088');
      }
    } catch (error) {
      console.log('Direct connection to API failed:', error.message);
      
      // Try port 8089 next
      try {
        const response = await axios.get('http://127.0.0.1:8089/api/v1/diagnostic/ping', {
          proxy: false,
          timeout: 2000,
          headers: {
            'Cache-Control': 'no-cache',
            'Pragma': 'no-cache'
          }
        });
        
        if (response.status === 200) {
          connectionInfo.apiAccessible = true;
          connectionInfo.apiPort = 8089;
          connectionInfo.error = 'API is running on the wrong port (8089). Please use port 8088.';
          console.log('API is running on the wrong port (8089)');
        }
      } catch (port8089Error) {
        // Both 8088 and 8089 failed with direct connection
        console.log('Both direct port connections failed');
        
        // Try with proxy bypass
        try {
          const response = await axios.get('/api/diagnostic/ping', {
            timeout: 2000
          });
          
          if (response.status === 200) {
            connectionInfo.apiConnected = true;
            console.log('Connected to API through Next.js proxy');
          }
        } catch (proxyError) {
          console.log('Next.js proxy connection failed:', proxyError.message);
          connectionInfo.error = 'Cannot connect to API server. Please ensure it is running.';
        }
      }
    }
    
    // If we have any kind of API access, test authentication
    if (connectionInfo.apiAccessible || connectionInfo.apiConnected) {
      try {
        // Try to get an existing token from localStorage first
        const existingToken = localStorage.getItem('token');
        if (existingToken) {
          // If we already have a token, consider auth as working
          connectionInfo.authWorking = true;
          console.log('Using existing authentication token');
        } else {
          // Otherwise try to get a new token
          const response = await axios.post(
            connectionInfo.apiPort === 8089 
              ? 'http://127.0.0.1:8089/api/v1/auth/login'
              : '/api/auth/login', 
            {
              username: 'test@example.com',
              password: 'password'
            },
            {
              proxy: false,
              timeout: 3000
            }
          );
          
          if (response.status === 200 && response.data.access_token) {
            connectionInfo.authWorking = true;
            console.log('Authentication is working');
            
            // Store the token for future use
            localStorage.setItem('token', response.data.access_token);
          }
        }
      } catch (authError) {
        console.log('Authentication test failed:', authError.message);
        // Only show error if we don't have another error and API is not connected
        if (!connectionInfo.error) {
          // Use more helpful message that doesn't block UI functionality
          connectionInfo.error = 'API connected but authentication needs attention.';
        }
      }
    }
  } catch (error) {
    console.error('API connection check error:', error);
    connectionInfo.error = `Error checking API connection: ${error.message}`;
  }
  
  return connectionInfo;
}

/**
 * Gets the current API status and returns a user-friendly status object
 * This is useful for displaying in the UI
 */
export function getAPIStatus(connectionInfo: ConnectionInfo): APIStatus {
  if (!connectionInfo.isOnline) {
    return {
      status: 'offline',
      statusText: 'Browser Offline',
      statusColor: 'red',
      message: 'Your browser is offline. Please check your internet connection.'
    };
  }
  
  if (connectionInfo.apiPort === 8089) {
    return {
      status: 'wrong-port',
      statusText: 'Wrong Port',
      statusColor: 'orange',
      message: 'API is running on the wrong port (8089). It should be on port 8088.'
    };
  }
  
  if (connectionInfo.apiAccessible || connectionInfo.apiConnected) {
    if (connectionInfo.authWorking) {
      return {
        status: 'connected',
        statusText: 'Connected',
        statusColor: 'green',
        message: 'API connection is working properly.'
      };
    } else {
      return {
        status: 'auth-issue',
        statusText: 'Auth Issue',
        statusColor: 'orange',
        message: 'Connected to API but authentication is not working.'
      };
    }
  }
  
  return {
    status: 'disconnected',
    statusText: 'Disconnected',
    statusColor: 'red',
    message: connectionInfo.error || 'Cannot connect to API server. Please ensure it is running.'
  };
}

/**
 * Resolves API accessibility issues by trying different methods
 * This can be used to fix connection issues automatically
 */
export async function resolveAPIAccessibility(): Promise<boolean> {
  // First, check current status
  const connectionInfo = await checkAPIConnection();
  
  // If already connected, nothing to do
  if (connectionInfo.apiAccessible && connectionInfo.apiPort === 8088) {
    return true;
  }
  
  // If wrong port, notify user
  if (connectionInfo.apiPort === 8089) {
    console.log('API is running on wrong port (8089). Please restart on port 8088.');
    return false;
  }
  
  // Try with additional headers to bypass proxy
  try {
    const response = await axios.get('http://127.0.0.1:8088/api/v1/diagnostic/ping', {
      proxy: false,
      timeout: 5000,
      headers: {
        'Cache-Control': 'no-cache',
        'Pragma': 'no-cache',
        'X-Requested-With': 'XMLHttpRequest',
        'Connection': 'keep-alive'
      }
    });
    
    if (response.status === 200) {
      console.log('Successfully connected with bypass headers');
      return true;
    }
  } catch (error) {
    console.log('Bypass headers approach failed:', error.message);
  }
  
  // As a last resort, try localhost instead of 127.0.0.1
  try {
    const response = await axios.get('http://localhost:8088/api/v1/diagnostic/ping', {
      proxy: false,
      timeout: 5000
    });
    
    if (response.status === 200) {
      console.log('Successfully connected using localhost instead of 127.0.0.1');
      // Store this preference for future use
      if (typeof localStorage !== 'undefined') {
        localStorage.setItem('preferLocalhost', 'true');
      }
      return true;
    }
  } catch (error) {
    console.log('Localhost approach failed:', error.message);
  }
  
  return false;
}
