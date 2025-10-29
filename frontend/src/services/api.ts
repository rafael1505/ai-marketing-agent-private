import axios from 'axios';

// Use relative URL to leverage Next.js proxy in development
// This will use the proxy rules defined in next.config.js
const API_URL = process.env.NEXT_PUBLIC_API_URL || '';
console.log('API_URL configured as:', API_URL);

// Generate correlation ID for request tracing
const generateCorrelationId = (): string => {
  return 'req_' + Math.random().toString(36).substr(2, 9) + '_' + Date.now().toString(36);
};

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
  // Base timeout for general API operations (can be overridden per request)
  // AI image generation uses dynamic timeout based on provider and image count
  timeout: 90000, // 90 seconds base timeout (increased from 60s)
});

// Add request interceptor to add the authorization token to the header
api.interceptors.request.use(
  (config) => {
    // Add correlation ID to every request
    const correlationId = generateCorrelationId();
    config.headers['X-Correlation-ID'] = correlationId;
    
    // Add timestamp for debugging
    console.log(`[${new Date().toISOString()}] API Request [${correlationId}]:`, {
      method: config.method?.toUpperCase(),
      url: config.url,
      baseURL: config.baseURL,
      fullURL: `${config.baseURL || ''}${config.url}`
    });
    
    const token = localStorage.getItem('token');
    if (token) {
      config.headers['Authorization'] = `Bearer ${token}`;
      console.log(`[${correlationId}] Adding auth token to request`);
    } else {
      console.log(`[${correlationId}] No auth token found`);
    }
    return config;
  },
  (error) => {
    console.error(`[${new Date().toISOString()}] Request interceptor error:`, error);
    return Promise.reject(error);
  }
);

// Add response interceptor to handle token expiration and other errors
api.interceptors.response.use(
  (response) => {
    const correlationId = response.config.headers['X-Correlation-ID'];
    console.log(`[${new Date().toISOString()}] API Success [${correlationId}]:`, {
      url: response.config.url,
      status: response.status,
      statusText: response.statusText
    });
    return response;
  },
  async (error) => {
    const correlationId = error.config?.headers?.['X-Correlation-ID'] || 'unknown';
    
    // Handle timeout errors specifically
    if (error.code === 'ECONNABORTED' || error.message.includes('timeout')) {
      console.error(`[${new Date().toISOString()}] Timeout Error [${correlationId}]:`, {
        message: 'Request timed out',
        url: error.config?.url,
        timeout: error.config?.timeout,
        isTimeout: true
      });
      
      // Enrich error with timeout information for user-friendly display
      error.isTimeout = true;
      error.userMessage = 'The request took too long to complete. The AI provider may be experiencing high load.';
      error.error_details = {
        error_type: 'timeout',
        message: `Request timeout after ${error.config?.timeout || 60000}ms`,
        user_message: 'errors.ai.timeout',
        provider: 'unknown',
        correlation_id: correlationId,
        timestamp: new Date().toISOString(),
        http_status: 408,
        suggested_actions: [
          'actions.try_again',
          'actions.try_different_provider',
          'actions.reduce_image_complexity'
        ],
        details: {
          timeout_seconds: (error.config?.timeout || 60000) / 1000,
          url: error.config?.url
        }
      };
      return Promise.reject(error);
    }
    
    // Handle network errors like connection refused
    if (error.message === 'Network Error' || !error.response) {
      console.error(`[${new Date().toISOString()}] Network Error [${correlationId}]:`, {
        message: error.message,
        url: error.config?.url,
        isConnectionError: true
      });
      error.isConnectionError = true;
      return Promise.reject(error);
    }
    
    console.error(`[${new Date().toISOString()}] API Error [${correlationId}]:`, {
      url: error.config?.url,
      status: error.response?.status,
      statusText: error.response?.statusText,
      data: error.response?.data
    });
    
    const originalRequest = error.config;
    
    // Handle auth errors - but don't redirect in development mode to allow demo data
    if (error.response?.status === 401 && !originalRequest._retry) {
      console.log(`[${correlationId}] Unauthorized access detected`);
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
          console.warn(`[${correlationId}] Failed to remove token from localStorage:`, storageError);
        }
        
        // Get current locale from URL or default to 'en'
        const locale = window.location.pathname.split('/')[1] || 'en';
        if (/^(en|pt)$/.test(locale)) {
          window.location.href = `/${locale}/login`;
        } else {
          window.location.href = '/en/login';
        }
      } else {
        console.log(`[${correlationId}] Development mode: Not redirecting to login, allowing service to handle with demo data`);
        // Add a flag to indicate this is an auth error in development
        error.isDevelopmentAuthError = true;
      }
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
    // Prepare the request configuration
    const config = {
      url,
      method: options.method,
      data: options.body,
      headers: options.headers
    };

    console.log('Making API request to:', url, 'with config:', config);
    
    // Make the API call
    const response = await api(config);
    console.log('API response received:', response.data);
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

// Initialize development token for local development
const initializeDevelopmentAuth = () => {
  if (typeof window === 'undefined') return; // Skip on server-side
  
  const isLocalhost = window.location.hostname === 'localhost' || 
                      window.location.hostname === '127.0.0.1';
  
  if (!isLocalhost) return;
  
  const currentToken = localStorage.getItem('token');
  const validDevToken = 'eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9.eyJzdWIiOiJ0ZXN0QGV4YW1wbGUuY29tIiwibmFtZSI6IlRlc3QgVXNlciIsInJvbGUiOiJhZG1pbiIsImlhdCI6MTc0ODYxNjIwNiwiZXhwIjoxNzUxMjA4MjA2fQ.5tet1p59rOC6bsn7hnyr-i3O-C42IyVJ1qevxLDwfYw';
  
  // Replace invalid tokens with valid development token
  if (!currentToken || currentToken.startsWith('mock_test_token')) {
    console.log('API service: Setting valid development JWT token');
    localStorage.setItem('token', validDevToken);
  }
};

// Initialize development auth
initializeDevelopmentAuth();

export default api;
