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
      {/* Floating button in bottom-right corner with clear label */}
      <div className="fixed bottom-6 right-6 z-50 flex items-center space-x-3">
        {/* Tooltip/Label */}
        <div className={`
          bg-white/95 backdrop-blur-sm text-gray-700 px-3 py-2 rounded-lg shadow-lg border text-sm font-medium
          transition-all duration-200 ${showDebugger ? 'opacity-100 translate-x-0' : 'opacity-0 translate-x-2 pointer-events-none'}
        `}>
          Style Debugger
        </div>
        
        {/* Button */}
        <button 
          className="group relative bg-white/95 backdrop-blur-sm hover:bg-white border border-gray-200 hover:border-blue-300 rounded-full p-3 shadow-lg hover:shadow-xl transition-all duration-200 transform hover:scale-105"
          onClick={() => setShowDebugger(!showDebugger)}
          title="Toggle Style Debugger (Alt+D)"
        >
          <svg 
            xmlns="http://www.w3.org/2000/svg" 
            width="22" 
            height="22" 
            viewBox="0 0 24 24" 
            fill="none" 
            stroke="currentColor" 
            strokeWidth="2" 
            strokeLinecap="round" 
            strokeLinejoin="round"
            className={`text-gray-600 group-hover:text-blue-600 transition-colors duration-200 ${showDebugger ? 'text-blue-600' : ''}`}
          >
            <circle cx="12" cy="12" r="3"/>
            <path d="M12 1v6m0 6v6"/>
            <path d="m9 12 3 3 3-3"/>
            <path d="M9 21h6"/>
            <path d="M12 3C8 3 5 6 5 10v4a2 2 0 0 0 2 2h10a2 2 0 0 0 2-2v-4c0-4-3-7-7-7Z"/>
          </svg>
          
          {/* Active indicator */}
          {showDebugger && (
            <div className="absolute -top-1 -right-1 w-3 h-3 bg-blue-500 rounded-full animate-pulse"></div>
          )}
        </button>
      </div>
      
      {/* Render the debugger if enabled */}
      {showDebugger && <StyleDebugger />}
    </>
  );
}
