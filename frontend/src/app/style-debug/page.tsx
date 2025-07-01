"use client";

import React, { useEffect, useRef } from 'react';
import { Card, CardHeader, CardTitle, CardDescription, CardContent, CardFooter } from "@/components/ui/card";
import { Button } from "@/components/ui/button";
import { gradientText, withHoverCard, withButtonScale, withFadeIn, debugElementStyles } from "@/lib/style-utils";
import { forceApplyCustomStyles } from "@/lib/force-styles";

export default function StyleDebugger() {
  const cardRef = useRef<HTMLDivElement>(null);
  const buttonRef = useRef<HTMLButtonElement>(null);
  
  useEffect(() => {
    // Force apply custom styles to ensure they work
    forceApplyCustomStyles();
    
    // Debug card and button styles when component mounts
    if (cardRef.current) {
      console.log('Card styles:');
      debugElementStyles(cardRef.current);
    }
    
    if (buttonRef.current) {
      console.log('Button styles:');
      debugElementStyles(buttonRef.current);
    }
    
    // Only add inspector in browser environment
    let styleInspector: HTMLDivElement | null = null;
    
    // Add a class inspector to help debug applied styles
    if (typeof window !== 'undefined' && typeof document !== 'undefined') {
      styleInspector = document.createElement('div');
      styleInspector.style.position = 'fixed';
      styleInspector.style.bottom = '10px';
      styleInspector.style.right = '10px';
      styleInspector.style.padding = '10px';
      styleInspector.style.background = 'rgba(0,0,0,0.7)';
      styleInspector.style.color = 'white';
      styleInspector.style.fontSize = '12px';
      styleInspector.style.zIndex = '9999';
      styleInspector.style.maxWidth = '300px';
      styleInspector.style.maxHeight = '150px';
      styleInspector.style.overflow = 'auto';
      
      const handleMouseOver = (e: MouseEvent) => {
        if (!styleInspector) return;
        const el = e.target as HTMLElement;
        styleInspector.innerHTML = `
          <div>Element: ${el.tagName}</div>
          <div>Classes: ${el.className}</div>
        `;
      };
      
      document.body.addEventListener('mouseover', handleMouseOver);
      document.body.appendChild(styleInspector);
      
      return () => {
        document.body.removeEventListener('mouseover', handleMouseOver);
        if (styleInspector && document.body.contains(styleInspector)) {
          document.body.removeChild(styleInspector);
        }
      };
    }
    
    return undefined;
  }, []);
  
  return (
    <div className="container mx-auto px-4 py-8">
      <h1 className="text-3xl font-bold mb-8">
        {gradientText("Style Debugger")}
      </h1>

      <div className="grid grid-cols-1 md:grid-cols-2 gap-6">
        {/* Test Card Styling */}
        <div>
          <h2 className="text-2xl font-semibold mb-4">Card Styles</h2>
          <Card className={withHoverCard("")} ref={cardRef}>
            <CardHeader>
              <CardTitle>Standard Card</CardTitle>
              <CardDescription>Testing hover animations and shadows</CardDescription>
            </CardHeader>
            <CardContent>
              <p>This card should have hover effects and elevation changes.</p>
            </CardContent>
            <CardFooter>
              <p className="text-sm text-muted-foreground">Hover over me!</p>
            </CardFooter>
          </Card>
        </div>

        {/* Test Button Styling */}
        <div>
          <h2 className="text-2xl font-semibold mb-4">Button Styles</h2>
          <div className="space-y-4">
            <Button className={withButtonScale("")} ref={buttonRef}>Primary Button</Button>
            <Button variant="ghost" className={withButtonScale("")}>Secondary Button</Button>
            <Button variant="outline" className={withButtonScale("")}>Outline Button</Button>
          </div>
        </div>

        {/* Test Gradient Text */}
        <div>
          <h2 className="text-2xl font-semibold mb-4">Gradient Text</h2>
          <div className="space-y-4">
            <h3 className="text-xl gradient-text">This text should have a gradient</h3>
            <p>Regular text for comparison</p>
            <h3 className="text-xl">{gradientText("Applied via helper function")}</h3>
          </div>
        </div>

        {/* Test Animations */}
        <div>
          <h2 className="text-2xl font-semibold mb-4">Animations</h2>
          <div className="space-y-4">
            <div className={withFadeIn("p-4 border rounded")}>
              <p>This element should fade in</p>
            </div>
            <div className="stagger-fade-in space-y-2">
              <p>Staggered item 1</p>
              <p>Staggered item 2</p>
              <p>Staggered item 3</p>
            </div>
            <div className="flex items-center gap-2">
              <span className="spinner"></span>
              <span>Loading spinner</span>
            </div>
          </div>
        </div>
      </div>

      {/* CSS Variables Test */}
      <div className="mt-8">
        <h2 className="text-2xl font-semibold mb-4">CSS Variables Test</h2>
        <div className="grid grid-cols-1 md:grid-cols-3 gap-4">
          <div className="bg-primary text-primary-foreground p-4 rounded">Primary Color</div>
          <div className="bg-secondary text-secondary-foreground p-4 rounded">Secondary Color</div>
          <div className="bg-accent text-accent-foreground p-4 rounded">Accent Color</div>
        </div>
      </div>
    </div>
  );
}
