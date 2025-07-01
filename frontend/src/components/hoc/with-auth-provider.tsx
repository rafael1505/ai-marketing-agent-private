"use client";

import { AuthProvider } from "@/contexts/auth-context";
import { useContext } from "react";
import { AuthContext } from "@/contexts/auth-context";
import { useEffect, useState } from "react";

// Higher-order component to ensure AuthProvider is always available
export function withAuthProvider<P extends object>(WrappedComponent: React.ComponentType<P>) {
  return function AuthProviderWrapper(props: P) {
    const [isClient, setIsClient] = useState(false);
    
    useEffect(() => {
      setIsClient(true);
    }, []);
    
    // Check if we're already inside an AuthProvider by checking the context directly
    const existingContext = useContext(AuthContext);
    const hasAuthContext = existingContext !== undefined;
    
    // If we're on the server or don't have auth context, wrap with AuthProvider
    if (!isClient || !hasAuthContext) {
      return (
        <AuthProvider>
          <WrappedComponent {...props} />
        </AuthProvider>
      );
    }
    
    // If we already have auth context, just render the component
    return <WrappedComponent {...props} />;
  };
}
