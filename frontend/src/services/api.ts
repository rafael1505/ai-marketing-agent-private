import axios from 'axios';

// Always use localhost for development to avoid CORS issues
// Fallback to port 8088 but allow override via environment variable
const API_URL = process.env.NEXT_PUBLIC_API_URL || 'http://127.0.0.1:8088/api/v1';
console.log('API_URL configured as:', API_URL);

// Add a flag to track API availability
export const apiStatus = {
  available: false,
  lastChecked: 0,
  checkingPromise: null as Promise<boolean> | null,
  async check(): Promise<boolean> {
    // Only check every 30 seconds
    const now = Date.now();
    if (now - this.lastChecked < 30000 && this.lastChecked > 0) {
      return this.available;
    }
    
    // If we're already checking, return that promise
    if (this.checkingPromise) {
      return this.checkingPromise;
    }
    
    // Start a new check
    this.checkingPromise = new Promise(async (resolve) => {
      try {
        // Create a timeout controller for Edge compatibility
        const controller = new AbortController();
        const timeoutId = setTimeout(() => controller.abort(), 2000);
        
        // Try a simple ping
        const result = await fetch(`${API_URL}/diagnostic/ping`, {
          method: 'GET',
          headers: { 'Content-Type': 'application/json' },
          // Short timeout to avoid hanging - Edge compatible
          signal: controller.signal
        });
        
        clearTimeout(timeoutId);
        this.available = result.ok;
        console.log(`API ${this.available ? 'is' : 'is NOT'} available`);
      } catch (error) {
        console.warn('API availability check failed:', error);
        this.available = false;
      } finally {
        this.lastChecked = now;
        this.checkingPromise = null;
        resolve(this.available);
      }
    });
    
    return this.checkingPromise;
  }
};

// Use environment variables to override proxy settings
if (typeof window !== 'undefined') {
  // Add this in browser environment to bypass corporate proxies for local development
  window.localStorage.setItem('bypassProxy', 'true');
}

const api = axios.create({
  baseURL: API_URL,
  headers: {
    'Content-Type': 'application/json',
  },
  // Disable proxy to use direct connection to local API
  proxy: false,
  // Increase timeout for network issues
  timeout: 15000,
});

// Add request interceptor to add the authorization token to the header
api.interceptors.request.use(
  (config) => {
    const token = localStorage.getItem('token');
    if (token) {
      config.headers['Authorization'] = `Bearer ${token}`;
    }
    return config;
  },
  (error) => {
    return Promise.reject(error);
  }
);

// Add response interceptor to handle token expiration and other errors
api.interceptors.response.use(
  (response) => {
    console.log(`API response: ${response.config.url} - Status: ${response.status}`);
    return response;
  },
  async (error) => {
    // Handle network errors like connection refused
    if (error.message === 'Network Error' || !error.response) {
      console.error('API network error:', error.message, 'for request:', error.config?.url);
      error.isConnectionError = true;
      return Promise.reject(error);
    }
    
    console.error('API error interceptor caught:', error.message);
    
    const originalRequest = error.config;
    
    // Handle auth errors - but don't redirect in development mode to allow demo data
    if (error.response?.status === 401 && !originalRequest._retry) {
      console.log('Unauthorized access detected');
      originalRequest._retry = true;
      
      // Edge-compatible development mode detection
      let isDevelopment = false;
      try {
        isDevelopment = process.env.NODE_ENV === 'development' || 
                       (typeof window !== 'undefined' && window.location && 
                        (window.location.hostname === 'localhost' ||
                         window.location.hostname === '127.0.0.1' ||
                         window.location.hostname.includes('localhost')));
      } catch (devError) {
        // Fallback: assume development if on localhost ports
        isDevelopment = typeof window !== 'undefined' && 
                       window.location && 
                       (window.location.port === '3000' || 
                        window.location.port === '3001');
      }
      
      if (!isDevelopment) {
        // Edge-compatible localStorage removal
        try {
          localStorage.removeItem('token');
        } catch (storageError) {
          console.warn('Failed to remove token from localStorage:', storageError);
        }
        
        // Get current locale from URL or default to 'en'
        const locale = window.location.pathname.split('/')[1] || 'en';
        if (/^(en|pt)$/.test(locale)) {
          window.location.href = `/${locale}/login`;
        } else {
          window.location.href = '/en/login';
        }
      } else {
        console.log('Development mode: Not redirecting to login, allowing service to handle with demo data');
        // Add a flag to indicate this is an auth error in development
        error.isDevelopmentAuthError = true;
      }
    }
    
    // Log other errors for debugging
    if (error.response) {
      console.error(`API error: ${originalRequest.url} - Status: ${error.response.status}`, error.response.data);
    } else if (error.request) {
      console.error('API request made but no response received:', error.request);
    }
    
    return Promise.reject(error);
  }
);

// General request wrapper for API calls with better error handling
export const apiRequest = async (
  url: string,
  options: { method: string; body?: any; headers?: Record<string, string> } = { method: "GET" }
): Promise<any> => {
  try {
    // Check API availability first if we haven't done it recently
    await apiStatus.check();
    
    // Prepare the request configuration
    const config = {
      url,
      method: options.method,
      data: options.body,
      headers: options.headers
    };

    // Make the API call
    const response = await api(config);
    return response.data;
  } catch (error) {
    console.error(`API request failed for ${url}:`, error);
    
    // If offline mode is enabled, return null for callers to handle
    if (!apiStatus.available) {
      console.log('API is unavailable, returning null to allow offline mode handling');
      return null;
    }
    
    throw error;
  }
};

export default api;
