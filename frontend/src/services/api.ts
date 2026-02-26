/**
 * API client layer for the frontend.
 *
 * Architectural decisions (see frontend/ARCHITECTURE.md):
 * - Isomorphic BASE_URL: client → localhost:8088, server (SSR/Docker) → web:8000.
 * - Every request gets a UUID X-Correlation-ID; errors carry normalizedErrorDetails (correlation_id, user_message).
 * - Request interceptor normalizes the URL path by stripping leading 'api/v1/' and 'api/' so that baseURL
 *   is never duplicated (prevents 404s when callers pass full paths instead of resource-relative paths).
 */
import axios from 'axios';
import type { ErrorDetails } from '@/types/api-errors';
import { isErrorDetails } from '@/types/api-errors';

declare module 'axios' {
  interface AxiosError {
    normalizedErrorDetails?: ErrorDetails;
    isTimeout?: boolean;
    isConnectionError?: boolean;
    isDevelopmentAuthError?: boolean;
  }
}

/** Isomorphic API base: client → localhost:8088, server → web:8000. No trailing slash (see ARCHITECTURE.md). */
const BASE_URL =
  typeof window !== 'undefined'
    ? 'http://localhost:8088/api/v1'   // Client-side
    : 'http://web:8000/api/v1';         // Server-side (Docker internal)

/** Generate a UUID for correlation ID (MCP contract). Uses crypto.randomUUID() when available, else RFC 4122 v4-style. */
export function generateCorrelationId(): string {
  if (typeof crypto !== 'undefined' && typeof crypto.randomUUID === 'function') {
    return crypto.randomUUID();
  }
  // Fallback for older environments: simple v4-style UUID
  return 'xxxxxxxx-xxxx-4xxx-yxxx-xxxxxxxxxxxx'.replace(/[xy]/g, (c) => {
    const r = (Math.random() * 16) | 0;
    const v = c === 'x' ? r : (r & 0x3) | 0x8;
    return v.toString(16);
  });
}

/** Build ErrorDetails for client-side failures (timeout, network/DNS). */
function buildClientErrorDetails(
  error_type: 'timeout' | 'network_error' | 'unknown_error',
  user_message: string,
  correlation_id: string,
  http_status: number,
  details: Record<string, unknown> = {}
): ErrorDetails {
  return {
    error_type,
    user_message,
    provider: 'unknown',
    correlation_id,
    http_status,
    details,
    timestamp: new Date().toISOString(),
    suggested_actions: ['actions.try_again', 'actions.try_different_provider'],
  };
}

/** Normalize backend error_details from response body; ensure correlation_id is UUID (from body or request header). */
function normalizeResponseError(
  data: unknown,
  requestCorrelationId: string,
  responseStatus?: number
): ErrorDetails {
  if (isErrorDetails(data)) {
    const cid = typeof data.correlation_id === 'string' && data.correlation_id.length > 0
      ? data.correlation_id
      : requestCorrelationId;
    return {
      ...data,
      correlation_id: cid,
      timestamp: data.timestamp ?? new Date().toISOString(),
    };
  }
  const raw = data as Record<string, unknown> | null | undefined;
  if (raw && typeof raw === 'object' && raw.error_details && isErrorDetails(raw.error_details)) {
    const ed = raw.error_details as ErrorDetails;
    const cid = typeof ed.correlation_id === 'string' && ed.correlation_id.length > 0
      ? ed.correlation_id
      : requestCorrelationId;
    return { ...ed, correlation_id: cid, timestamp: ed.timestamp ?? new Date().toISOString() };
  }
  return buildClientErrorDetails(
    'unknown_error',
    'errors.ai.unknown_error',
    requestCorrelationId,
    responseStatus ?? 500,
    raw && typeof raw === 'object' && raw.details ? (raw.details as Record<string, unknown>) : {}
  );
}

/** Get correlation_id and user_message from an API error for logging (avoids minified "Q" in console). */
export function getErrorLogContext(error: unknown): { correlation_id?: string; user_message?: string } {
  if (!error || typeof error !== 'object') return {};
  const ax = error as Record<string, unknown>;
  // Prefer normalizedErrorDetails (set by response interceptor); use bracket so minified builds still find it
  const details = ax['normalizedErrorDetails'] as ErrorDetails | undefined;
  if (details && typeof details === 'object' && typeof details.correlation_id === 'string') {
    return {
      correlation_id: details.correlation_id,
      user_message: typeof details.user_message === 'string' ? details.user_message : undefined,
    };
  }
  // Fallback: read X-Correlation-ID from request config (set by request interceptor)
  const config = ax['config'] as { headers?: Record<string, string> } | undefined;
  const cid = config?.headers?.['X-Correlation-ID'];
  if (typeof cid === 'string' && cid.length > 0) {
    return { correlation_id: cid, user_message: undefined };
  }
  return {};
}

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
        const result = await fetch(`${BASE_URL}/diagnostic/ping`, {
          method: 'GET',
          headers: { 'Content-Type': 'application/json' },
          // Short timeout to avoid hanging - Edge compatible
          signal: controller.signal
        });
        
        clearTimeout(timeoutId);
        this.available = result.ok;
      } catch {
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
  baseURL: BASE_URL,
  headers: {
    'Content-Type': 'application/json',
  },
  // Disable proxy to use direct connection to local API
  proxy: false,
  // Base timeout for general API operations (can be overridden per request)
  // AI image generation uses dynamic timeout based on provider and image count
  timeout: 90000, // 90 seconds base timeout (increased from 60s)
});

/**
 * Request interceptor: X-Correlation-ID injection and defensive URL normalization.
 *
 * URL normalization (defensive architecture): Developers may pass full paths (e.g. "/api/v1/materials"
 * or "/api/notifications/unread-count") instead of resource-relative paths. Because baseURL is already
 * ".../api/v1", combining would duplicate the segment and cause 404s. We strip leading 'api/v1/' and
 * 'api/' in a loop until the path is resource-relative (e.g. "materials", "notifications/unread-count"),
 * so the final URL is always baseURL + "/" + path. See frontend/ARCHITECTURE.md and
 * specs/005-materials-page-stability/api-normalization-layer.md.
 */
api.interceptors.request.use(
  (config) => {
    if (config.url && typeof config.url === 'string') {
      let u = config.url.replace(/^\/+/, '');
      while (u.startsWith('api/v1/')) u = u.slice(7);
      while (u.startsWith('api/')) u = u.slice(4);
      config.url = u;
    }
    const existing = config.headers?.['X-Correlation-ID'];
    const correlationId =
      typeof existing === 'string' && existing.length > 0 ? existing : generateCorrelationId();
    config.headers['X-Correlation-ID'] = correlationId;
    let token: string | null = null;
    if (typeof window !== 'undefined') {
      try {
        token = localStorage.getItem('token');
      } catch {
        // SSR or restricted environment; skip auth header (005: init must not crash)
      }
    }
    if (token) {
      config.headers['Authorization'] = `Bearer ${token}`;
    }
    return config;
  },
  (error) => Promise.reject(error)
);

// Add response interceptor to handle token expiration and other errors
api.interceptors.response.use(
  (response) => response,
  async (error) => {
    const requestCorrelationId =
      (error.config?.headers?.['X-Correlation-ID'] as string) ?? generateCorrelationId();

    // Timeout: no response
    if (error.code === 'ECONNABORTED' || error.message?.includes('timeout')) {
      const details: ErrorDetails = buildClientErrorDetails(
        'timeout',
        'errors.ai.timeout',
        requestCorrelationId,
        408,
        {
          timeout_seconds: (error.config?.timeout ?? 60000) / 1000,
          url: error.config?.url,
        }
      );
      error.isTimeout = true;
      error.normalizedErrorDetails = details;
      return Promise.reject(error);
    }

    // Network/DNS: no response
    if (error.message === 'Network Error' || !error.response) {
      const details: ErrorDetails = buildClientErrorDetails(
        'network_error',
        'errors.ai.network_error',
        requestCorrelationId,
        503,
        { url: error.config?.url }
      );
      error.isConnectionError = true;
      error.normalizedErrorDetails = details;
      return Promise.reject(error);
    }

    // 4xx/5xx with response body
    const responseData = error.response?.data;
    const normalized: ErrorDetails = normalizeResponseError(
      responseData,
      requestCorrelationId,
      error.response?.status
    );
    error.normalizedErrorDetails = normalized;

    const originalRequest = error.config;

    if (error.response?.status === 401 && !originalRequest._retry) {
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
        } catch {
          // ignore
        }
        
        // Get current locale from URL or default to 'en'
        const locale = window.location.pathname.split('/')[1] || 'en';
        if (/^(en|pt)$/.test(locale)) {
          window.location.href = `/${locale}/login`;
        } else {
          window.location.href = '/en/login';
        }
      } else {
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
    const config = {
      url,
      method: options.method,
      data: options.body,
      headers: options.headers
    };
    const response = await api(config);
    return response.data;
  } catch (error) {
    if (!apiStatus.available) {
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
  
  if (!currentToken || currentToken.startsWith('mock_test_token')) {
    localStorage.setItem('token', validDevToken);
  }
};

// Initialize development auth
initializeDevelopmentAuth();

export default api;
