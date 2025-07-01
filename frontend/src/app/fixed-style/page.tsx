"use client";

import React, { useEffect, useState } from 'react';
import { Button } from '@/components/ui/button';
import { Card, CardHeader, CardTitle, CardContent, CardFooter } from '@/components/ui/card';
import { forceApplyCustomStyles } from '@/lib/force-styles';

// Client-side only component for debugging styles
const StyleDebugger = () => {
  const [isClient, setIsClient] = useState(false);
  const [styleInfo, setStyleInfo] = useState({
    primary: '',
    transition: '',
    bodyClasses: ''
  });

  // First, set a flag to indicate we're on the client
  useEffect(() => {
    setIsClient(true);
  }, []);

  // Then, only access browser APIs once we're on the client
  useEffect(() => {
    if (isClient) {
      setStyleInfo({
        primary: getComputedStyle(document.documentElement).getPropertyValue('--primary'),
        transition: getComputedStyle(document.documentElement).getPropertyValue('--transition-medium'),
        bodyClasses: document.body.className
      });
    }
  }, [isClient]);

  // If not client, render a placeholder with the same structure
  // This ensures consistent server/client rendering
  if (!isClient) {
    return (
      <pre className="p-4 bg-gray-100 rounded text-sm overflow-auto">
        <span>Loading style information...</span>
      </pre>
    );
  }

  return (
    <pre className="p-4 bg-gray-100 rounded text-sm overflow-auto">
      {`
CSS Variables:
--primary: ${styleInfo.primary}
--transition-medium: ${styleInfo.transition}

Body Classes: ${styleInfo.bodyClasses}
      `}
    </pre>
  );
};

export default function StyleFixedPage() {
  useEffect(() => {
    // Apply force styles on mount
    forceApplyCustomStyles();
  }, []);
  
  return (
    <div className="container mx-auto px-4 py-8">
      <h1 className="text-3xl font-bold mb-6 directGradientText">
        Fixed Styling Test Page
      </h1>
      
      <p className="mb-8">
        This page is designed to test our comprehensive styling fixes.
      </p>
      
      <div className="grid grid-cols-1 md:grid-cols-2 gap-8">
        {/* Test Card 1: With Direct Styles */}
        <div>
          <h2 className="text-xl font-medium mb-3">Card with Direct Styles</h2>
          <Card className="directHoverCard">
            <CardHeader>
              <CardTitle className="directGradientText">Direct Styled Card</CardTitle>
            </CardHeader>
            <CardContent>
              <p>This card uses the directHoverCard class for hover effects.</p>
            </CardContent>
            <CardFooter>
              <Button className="directBtnScale">Direct Styled Button</Button>
            </CardFooter>
          </Card>
        </div>
        
        {/* Test Card 2: With regular class names */}
        <div>
          <h2 className="text-xl font-medium mb-3">Card with Regular Classes</h2>
          <Card className="hover-card">
            <CardHeader>
              <CardTitle className="gradient-text">Regular Card</CardTitle>
            </CardHeader>
            <CardContent>
              <p>This card uses the hover-card class for hover effects.</p>
            </CardContent>
            <CardFooter>
              <Button className="btn-scale">Regular Button</Button>
            </CardFooter>
          </Card>
        </div>
        
        {/* Test Card 3: With inline styles */}
        <div>
          <h2 className="text-xl font-medium mb-3">Card with Inline Styles</h2>
          <Card style={{
            transition: "transform 0.3s, box-shadow 0.3s",
          }}
          onMouseOver={(e) => {
            e.currentTarget.style.transform = 'translateY(-4px)';
            e.currentTarget.style.boxShadow = '0 20px 25px -5px rgba(0, 0, 0, 0.1)';
          }}
          onMouseOut={(e) => {
            e.currentTarget.style.transform = '';
            e.currentTarget.style.boxShadow = '';
          }}>
            <CardHeader>
              <CardTitle style={{
                background: "linear-gradient(90deg, #3B82F6, #C026D3)",
                WebkitBackgroundClip: "text",
                WebkitTextFillColor: "transparent",
              }}>Inline Styled Card</CardTitle>
            </CardHeader>
            <CardContent>
              <p>This card uses inline styles for hover effects.</p>
            </CardContent>
            <CardFooter>
              <Button style={{
                transition: "transform 0.15s",
              }}
              onMouseOver={(e) => {
                e.currentTarget.style.transform = 'scale(1.03)';
              }}
              onMouseOut={(e) => {
                e.currentTarget.style.transform = '';
              }}>Inline Styled Button</Button>
            </CardFooter>
          </Card>
        </div>
        
        {/* Animation Test */}
        <div>
          <h2 className="text-xl font-medium mb-3">Animation Test</h2>
          <Card>
            <CardContent className="space-y-4">
              <div className="p-4 bg-gray-100 rounded directFadeIn">
                <p>This should fade in (direct class)</p>
              </div>
              <div className="p-4 bg-gray-100 rounded fade-in">
                <p>This should fade in (regular class)</p>
              </div>
              <div className="p-4 bg-gray-100 rounded animate-fadeIn">
                <p>This should fade in (Tailwind animation)</p>
              </div>
              <div className="p-4 bg-gray-100 rounded" 
                style={{animation: 'fadeIn 0.5s forwards'}}>
                <p>This should fade in (inline style)</p>
              </div>
            </CardContent>
          </Card>
        </div>
      </div>
      
      <div className="mt-8">
        <h2 className="text-xl font-medium mb-3">Style Debugging Info</h2>
        <StyleDebugger />
      </div>
    </div>
  );
}
