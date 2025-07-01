"use client";

import React from "react";

export function StyleDebugger() {
  const [cssVars, setCssVars] = React.useState<Record<string, string>>({});
  const [tailwindColors, setTailwindColors] = React.useState<string[]>([]);
  
  React.useEffect(() => {
    // Get CSS variables from root
    const computedStyle = getComputedStyle(document.documentElement);
    const vars: Record<string, string> = {};
    
    // Extract CSS variables
    for (let i = 0; i < computedStyle.length; i++) {
      const prop = computedStyle[i];
      if (prop.startsWith('--')) {
        vars[prop] = computedStyle.getPropertyValue(prop).trim();
      }
    }
    
    setCssVars(vars);
    
    // Extract Tailwind colors
    const colors = [
      'primary', 'secondary', 'accent', 'muted', 
      'background', 'foreground', 'border'
    ];
    setTailwindColors(colors);
    
  }, []);
  
  return (
    <div className="fixed bottom-4 right-4 p-4 bg-white dark:bg-gray-800 border rounded-lg shadow-lg z-50 max-w-md max-h-[80vh] overflow-auto">
      <h2 className="text-lg font-bold mb-2">Style Debug Panel</h2>
      
      <div className="mb-4">
        <h3 className="text-md font-semibold mb-2">Color Palette</h3>
        <div className="grid grid-cols-2 gap-2">
          {tailwindColors.map(color => (
            <div key={color} className="flex items-center">
              <div 
                className={`w-6 h-6 rounded mr-2 bg-${color}`} 
                title={`bg-${color}`}
              />
              <span className="text-xs">{color}</span>
            </div>
          ))}
        </div>
      </div>
      
      <div>
        <h3 className="text-md font-semibold mb-2">CSS Variables</h3>
        <div className="text-xs">
          {Object.entries(cssVars).map(([key, value]) => (
            <div key={key} className="grid grid-cols-2 mb-1">
              <span className="font-mono">{key}:</span>
              <span className="font-mono">{value}</span>
            </div>
          ))}
        </div>
      </div>
      
      <button 
        className="mt-4 px-2 py-1 text-xs bg-gray-200 dark:bg-gray-700 rounded"
        onClick={() => {
          const element = document.querySelector('[data-style-debugger]');
          if (element) {
            element.remove();
          }
        }}
      >
        Close
      </button>
    </div>
  );
}