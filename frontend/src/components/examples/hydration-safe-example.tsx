'use client';

import React from 'react';
import { useClientSide, useLocalStorage } from '@/hooks/use-client-side';

/**
 * Example component demonstrating how to use the useClientSide hook
 * to prevent React hydration errors when using browser APIs
 */
export function HydrationSafeExample() {
  const { isClient } = useClientSide();
  const { value: theme, setValue: setTheme, isLoading } = useLocalStorage('ui-theme', 'light');
  
  // Safe to access window only after client detection
  const [windowSize, setWindowSize] = React.useState({ width: 0, height: 0 });
  
  React.useEffect(() => {
    if (!isClient) return;
    
    const updateSize = () => {
      setWindowSize({
        width: window.innerWidth,
        height: window.innerHeight
      });
    };
    
    // Set initial size
    updateSize();
    
    // Listen for resize events
    window.addEventListener('resize', updateSize);
    
    // Cleanup
    return () => window.removeEventListener('resize', updateSize);
  }, [isClient]);
  
  // During server render and initial client render, show a loading state
  // This ensures consistent output between server and client
  if (!isClient || isLoading) {
    return (
      <div className="p-4 border rounded-lg">
        <h2 className="text-lg font-semibold mb-2">Hydration-Safe Component</h2>
        <div className="h-20 bg-gray-100 animate-pulse rounded flex items-center justify-center">
          <span>Loading client state...</span>
        </div>
      </div>
    );
  }
  
  // Only render the full component with dynamic values after hydration is complete
  return (
    <div className="p-4 border rounded-lg">
      <h2 className="text-lg font-semibold mb-2">Hydration-Safe Component</h2>
      <div className="flex flex-col gap-2">
        <div>
          <strong>Current theme:</strong> {theme}
        </div>
        <div>
          <strong>Window size:</strong> {windowSize.width} x {windowSize.height}
        </div>
        <div className="mt-2">
          <label className="block text-sm mb-1">Theme Preference:</label>
          <select 
            value={theme}
            onChange={(e) => setTheme(e.target.value)}
            className="px-2 py-1 border rounded"
          >
            <option value="light">Light</option>
            <option value="dark">Dark</option>
            <option value="system">System</option>
          </select>
        </div>
      </div>
    </div>
  );
}
