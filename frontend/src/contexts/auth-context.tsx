"use client";

import React, { createContext, useContext, useState, useEffect, ReactNode } from 'react';
import { useRouter } from 'next/navigation'; // Corrected import for App Router

interface AuthContextType {
  isLoggedIn: boolean;
  token: string | null;
  login: (token: string, locale: string) => void;
  logout: (locale: string) => void;
  isLoading: boolean;
}

const AuthContext = createContext<AuthContextType | undefined>(undefined);

// Export the context for HOCs to use
export { AuthContext };

export const AuthProvider: React.FC<{ children: ReactNode }> = ({ children }) => {
  // Track if we're in browser environment
  const [isClient, setIsClient] = useState(false);
  const [token, setToken] = useState<string | null>(null);
  const [isLoading, setIsLoading] = useState(true);
  const router = useRouter();

  // First effect: Just detect client-side rendering
  useEffect(() => {
    setIsClient(true);
  }, []);
  
  // Second effect: Only access localStorage after client detection
  useEffect(() => {
    if (!isClient) return;
    
    console.log("AuthProvider: initializing");
    try {
      const storedToken = localStorage.getItem('token');
      console.log("AuthProvider: token from storage:", storedToken ? "TOKEN_FOUND" : "NO_TOKEN");
      if (storedToken) {
        setToken(storedToken);
      }
    } catch (error) {
      console.error("Error accessing localStorage:", error);
    } finally {
      setIsLoading(false);
    }
  }, [isClient]);

  const login = (newToken: string, locale: string) => {
    console.log("Auth context login called with token:", newToken ? "TOKEN_RECEIVED" : "NO_TOKEN", "locale:", locale);
    
    // Only perform browser operations if we're on the client
    if (isClient) {
      // Check if this is a mock token for test users during development
      const isTestToken = newToken && newToken.startsWith('mock_test_token_');
      if (isTestToken) {
        console.log("Test token detected - using special development mode");
        // Store test flag in localStorage
        localStorage.setItem('isTestMode', 'true');
      }
      
      // First update the token in localStorage
      localStorage.setItem('token', newToken);
      console.log("Token saved to localStorage");
    } else {
      console.log("Login called during server render - deferring localStorage operations");
    }
    
    // Update the state (works in both environments)
    setToken(newToken);
    console.log("Token state updated in context");
    
    // Handle navigation (client-side only)
    if (isClient) {
      // Schedule navigation to happen after state update is processed
      const targetUrl = `/${locale}/dashboard`;
      console.log("Scheduling redirect to:", targetUrl);
      
      // Use setTimeout to ensure this happens after the current execution context
      setTimeout(() => {
        try {
          console.log("Executing router.push to:", targetUrl);
          router.push(targetUrl);
        } catch (error) {
          console.error("Router.push failed, using window.location.href instead:", error);
          window.location.href = targetUrl;
        }
      }, 100);
    }
  };

  const logout = (locale: string) => {
    // Only access localStorage on client
    if (isClient) {
      localStorage.removeItem('token');
    }
    
    // Update state
    setToken(null);
    
    // Handle navigation (client-side only)
    if (isClient) {
      // Ensure redirection happens after state update
      setTimeout(() => {
        router.push(`/${locale}/login`);
      }, 0);
    }
  };

  // For server-side rendering, we need safe default values
  // that won't trigger auth-dependent UI until hydration is complete
  return (
    <AuthContext.Provider 
      value={{ 
        // Only consider logged in if we've confirmed on client AND have a token
        isLoggedIn: isClient && !!token, 
        token, 
        login, 
        logout, 
        // Keep loading true until client hydration complete
        isLoading: !isClient || isLoading 
      }}
    >
      {children}
    </AuthContext.Provider>
  );
};

export const useAuth = (): AuthContextType => {
  const context = useContext(AuthContext);
  if (context === undefined) {
    // Check for development mode more reliably
    const isDevelopment = typeof window !== 'undefined' 
      ? (window.location.hostname === 'localhost' || window.location.hostname === '127.0.0.1')
      : process.env.NODE_ENV === 'development';
    
    // In development mode, provide a fallback to prevent crashes
    if (isDevelopment) {
      console.warn('useAuth called outside AuthProvider - providing development fallback');
      return {
        isLoggedIn: false,
        token: null,
        login: () => {},
        logout: () => {},
        isLoading: false
      };
    }
    throw new Error('useAuth must be used within an AuthProvider');
  }
  return context;
};
