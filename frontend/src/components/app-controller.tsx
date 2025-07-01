"use client";

import React from 'react';
import { StyleDebugger } from '@/components/ui/style-debugger';
import { forceApplyCustomStyles } from '@/lib/force-styles';

export function AppController() {
  const [showDebugger, setShowDebugger] = React.useState(false);
  
  // Setup keyboard shortcut to toggle debugger and apply force styles
  React.useEffect(() => {
    // Force apply custom styles to ensure consistent styling
    forceApplyCustomStyles();
    
    const handleKeyDown = (event: KeyboardEvent) => {
      // Alt + D to toggle debugger
      if (event.altKey && event.key === 'd') {
        setShowDebugger(prev => !prev);
      }
      // Alt + S to force apply styles
      if (event.altKey && event.key === 's') {
        forceApplyCustomStyles();
        console.log('Styles force-applied manually');
      }
    };
    
    window.addEventListener('keydown', handleKeyDown);
    return () => {
      window.removeEventListener('keydown', handleKeyDown);
    };
  }, []);
  
  return (
    <>
      {/* Floating button in bottom-left corner */}
      <button 
        className="fixed bottom-4 left-4 z-50 p-2 bg-primary/10 hover:bg-primary/20 rounded-full shadow-sm"
        onClick={() => setShowDebugger(!showDebugger)}
        title="Toggle Style Debugger (Alt+D)"
      >
        <svg 
          xmlns="http://www.w3.org/2000/svg" 
          width="20" 
          height="20" 
          viewBox="0 0 24 24" 
          fill="none" 
          stroke="currentColor" 
          strokeWidth="2" 
          strokeLinecap="round" 
          strokeLinejoin="round"
          className="text-primary"
        >
          <circle cx="12" cy="12" r="10"/>
          <path d="M12 16v-4"/>
          <path d="M12 8h.01"/>
        </svg>
      </button>
      
      {/* Render the debugger if enabled */}
      {showDebugger && <StyleDebugger />}
    </>
  );
}
