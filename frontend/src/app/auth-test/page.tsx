"use client";

import React from "react";
import { AuthProvider } from "@/contexts/auth-context";
import { useAuth } from "@/contexts/auth-context";

function AuthTestContent() {
  const auth = useAuth();
  
  return (
    <div className="p-8">
      <h1 className="text-2xl font-bold mb-4">Auth Test Page</h1>
      <div className="space-y-2">
        <p>User: {auth.user ? JSON.stringify(auth.user) : 'Not authenticated'}</p>
        <p>Is Authenticated: {auth.isAuthenticated ? 'Yes' : 'No'}</p>
        <p>Is Loading: {auth.isLoading ? 'Yes' : 'No'}</p>
      </div>
    </div>
  );
}

export default function AuthTestPage() {
  return (
    <AuthProvider>
      <AuthTestContent />
    </AuthProvider>
  );
}
