"use client";

import React, { useEffect, useState } from "react";
import { useRouter } from "next/navigation";

interface AuthProtectionProps {
  children: React.ReactNode;
  locale: string;
}

export default function AuthProtection({ children, locale }: AuthProtectionProps) {
  const router = useRouter();
  // Phase 1: Client detection
  const [isClient, setIsClient] = useState(false);
  // Phase 2: Authentication loading
  const [isLoading, setIsLoading] = useState(true);
  // Phase 3: Authentication status
  const [isAuthenticated, setIsAuthenticated] = useState(false);

  // First effect: Just detect client
  useEffect(() => {
    setIsClient(true);
  }, []);

  // Second effect: Check auth status only on client
  useEffect(() => {
    // Only check auth after confirming we're on client
    if (!isClient) return;

    try {
      // Edge-compatible localStorage access
      let token: string | null = null;
      try {
        token = localStorage.getItem("token");
      } catch (storageError) {
        console.warn("localStorage access failed:", storageError);
      }
      
      // Edge-compatible development mode detection
      let isDevelopment = false;
      try {
        isDevelopment = process.env.NODE_ENV === 'development' || 
                       (typeof window !== 'undefined' && window.location && 
                        (window.location.hostname === 'localhost' ||
                         window.location.hostname === '127.0.0.1' ||
                         window.location.hostname.includes('localhost')));
      } catch (devError) {
        console.warn("Development mode detection failed:", devError);
        // Fallback: assume development if on localhost ports
        isDevelopment = typeof window !== 'undefined' && 
                       window.location && 
                       (window.location.port === '3000' || 
                        window.location.port === '3001');
      }
      
      if (!token) {
        if (isDevelopment) {
          console.log("AuthProtection: No token found, but in development mode - allowing access with demo data");
          setIsAuthenticated(true);
          setIsLoading(false);
        } else {
          console.log("AuthProtection: No token found, redirecting to login");
          router.push(`/${locale}/login`);
        }
      } else {
        console.log("AuthProtection: Token found, allowing access");
        setIsAuthenticated(true);
        setIsLoading(false);
      }
    } catch (error) {
      console.error("AuthProtection: Error checking authentication", error);
      
      // Edge-compatible development mode detection for error handling
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
      
      if (isDevelopment) {
        console.log("AuthProtection: Error in development mode - allowing access with demo data");
        setIsAuthenticated(true);
        setIsLoading(false);
      } else {
        // Fallback to login on errors in production
        router.push(`/${locale}/login`);
      }
    }
  }, [isClient, router, locale]);

  // During server render and initial client render before hydration
  if (!isClient || isLoading) {
    return (
      <div className="flex justify-center items-center h-screen">
        <div className="animate-spin rounded-full h-12 w-12 border-b-2 border-primary"></div>
      </div>
    );
  }

  // Only render children after confirming auth on client
  return isAuthenticated ? <>{children}</> : null;
}
