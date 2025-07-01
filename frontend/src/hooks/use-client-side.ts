'use client';

import { useState, useEffect } from 'react';

/**
 * Hook to safely handle client-side only code and prevent hydration mismatches
 * 
 * This hook implements the two-phase rendering pattern:
 * 1. Returns `{ isClient: false }` during server rendering and initial client render
 * 2. Returns `{ isClient: true }` after hydration is complete
 * 
 * @example
 * ```tsx
 * function MyComponent() {
 *   const { isClient } = useClientSide();
 *   
 *   // Only access browser APIs after client detection
 *   const [data, setData] = useState(null);
 *   
 *   useEffect(() => {
 *     if (isClient) {
 *       // Safe to access localStorage, window, etc.
 *       const storedValue = localStorage.getItem('my-key');
 *       setData(storedValue);
 *     }
 *   }, [isClient]);
 *   
 *   // Server-safe rendering
 *   if (!isClient) {
 *     return <div>Loading...</div>;
 *   }
 *   
 *   // Client-only rendering
 *   return <div>Client data: {data}</div>;
 * }
 * ```
 */
export function useClientSide() {
  const [isClient, setIsClient] = useState(false);
  
  useEffect(() => {
    setIsClient(true);
  }, []);
  
  return { isClient };
}

/**
 * Hook for accessing browser storage safely without hydration mismatches
 * 
 * @param key - The localStorage key to access
 * @param initialValue - The default value to use if key doesn't exist
 * @example
 * ```tsx
 * function ProfileSettings() {
 *   const { value: theme, setValue: setTheme, isLoading } = useLocalStorage('theme', 'light');
 *   
 *   if (isLoading) return <div>Loading preferences...</div>;
 *   
 *   return (
 *     <select value={theme} onChange={(e) => setTheme(e.target.value)}>
 *       <option value="light">Light</option>
 *       <option value="dark">Dark</option>
 *     </select>
 *   );
 * }
 * ```
 */
export function useLocalStorage<T>(key: string, initialValue: T) {
  const { isClient } = useClientSide();
  const [value, setValue] = useState<T>(initialValue);
  const [isLoading, setIsLoading] = useState(true);
  
  // Load value from localStorage when on client
  useEffect(() => {
    if (isClient) {
      try {
        const item = localStorage.getItem(key);
        setValue(item ? JSON.parse(item) : initialValue);
      } catch (error) {
        console.error(`Error reading localStorage key "${key}":`, error);
        setValue(initialValue);
      } finally {
        setIsLoading(false);
      }
    }
  }, [isClient, key, initialValue]);
  
  // Update localStorage when value changes
  const updateValue = (newValue: T | ((val: T) => T)) => {
    try {
      const valueToStore = newValue instanceof Function ? newValue(value) : newValue;
      setValue(valueToStore);
      
      if (isClient) {
        localStorage.setItem(key, JSON.stringify(valueToStore));
      }
    } catch (error) {
      console.error(`Error setting localStorage key "${key}":`, error);
    }
  };
  
  return { 
    value, 
    setValue: updateValue, 
    isLoading: !isClient || isLoading,
    isClient
  };
}

/**
 * Hook for safely using authentication state with hydration safety
 * 
 * This wraps the regular auth context with client-side detection to prevent
 * hydration mismatches.
 * 
 * @example
 * ```tsx
 * function NavBar() {
 *   const { isAuthenticated, isLoading } = useAuthClientSafe();
 *   
 *   if (isLoading) {
 *     return <nav>Loading...</nav>;
 *   }
 *   
 *   return (
 *     <nav>
 *       {isAuthenticated ? (
 *         <button>Logout</button>
 *       ) : (
 *         <button>Login</button>
 *       )}
 *     </nav>
 *   );
 * }
 * ```
 */
export function useAuthClientSafe() {
  const { isClient } = useClientSide();
  
  // Note: This is a placeholder for the actual auth context
  // You would replace this with your actual auth context usage
  const [isAuthenticated, setIsAuthenticated] = useState(false);
  const [authToken, setAuthToken] = useState<string | null>(null);
  const [isAuthLoading, setIsAuthLoading] = useState(true);
  
  // Load authentication state on client
  useEffect(() => {
    if (isClient) {
      try {
        const token = localStorage.getItem('token');
        setAuthToken(token);
        setIsAuthenticated(!!token);
      } catch (error) {
        console.error('Error reading auth state:', error);
      } finally {
        setIsAuthLoading(false);
      }
    }
  }, [isClient]);
  
  return {
    isAuthenticated: isClient && isAuthenticated,
    authToken,
    isLoading: !isClient || isAuthLoading,
    isClient
  };
}
