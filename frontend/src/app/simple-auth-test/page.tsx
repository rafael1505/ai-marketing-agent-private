"use client";

import React from "react";
import { useAuth } from "@/contexts/auth-context";

export default function SimpleAuthTestPage() {
  const [authState, setAuthState] = React.useState<any>(null);
  const [error, setError] = React.useState<string | null>(null);
  
  React.useEffect(() => {
    try {
      const auth = useAuth();
      setAuthState(auth);
      setError(null);
    } catch (err) {
      setError(err instanceof Error ? err.message : String(err));
    }
  }, []);
  
  return (
    <div className="p-8">
      <h1 className="text-2xl font-bold mb-4">Simple Auth Test</h1>
      
      {error ? (
        <div className="bg-red-100 border border-red-400 text-red-700 px-4 py-3 rounded mb-4">
          <strong>Error:</strong> {error}
        </div>
      ) : (
        <div className="bg-green-100 border border-green-400 text-green-700 px-4 py-3 rounded mb-4">
          <strong>Success:</strong> useAuth hook is working!
        </div>
      )}
      
      {authState && (
        <div className="mt-4">
          <h2 className="text-lg font-semibold">Auth State:</h2>
          <pre className="bg-gray-100 p-4 rounded mt-2 text-sm">
            {JSON.stringify(authState, null, 2)}
          </pre>
        </div>
      )}
    </div>
  );
}
