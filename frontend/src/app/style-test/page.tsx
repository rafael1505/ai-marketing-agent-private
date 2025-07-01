"use client";

import React from "react";
import { Card, CardHeader, CardTitle, CardContent } from "@/components/ui/card";
import { Button } from "@/components/ui/button";
import { StyleDebugger } from "@/components/ui/style-debugger";

export default function StyleTestPage() {
  const [showDebugger, setShowDebugger] = React.useState(false);
  
  return (
    <div className="p-8 space-y-8">
      <div className="flex items-center justify-between">
        <h1 className="text-3xl font-bold tracking-tight">Style Test Page</h1>
        <Button 
          onClick={() => setShowDebugger(!showDebugger)}
          variant="outline"
        >
          {showDebugger ? "Hide" : "Show"} Style Debugger
        </Button>
      </div>

      <div className="grid gap-8">
        {/* Test Section: Typography */}
        <Card>
          <CardHeader>
            <CardTitle>Typography</CardTitle>
          </CardHeader>
          <CardContent className="space-y-4">
            <h1 className="text-4xl font-bold">Heading 1</h1>
            <h2 className="text-3xl font-semibold">Heading 2</h2>
            <h3 className="text-2xl font-medium">Heading 3</h3>
            <h4 className="text-xl font-medium">Heading 4</h4>
            <p className="text-base">Normal paragraph text</p>
            <p className="text-sm">Small text</p>
            <p className="text-xs">Extra small text</p>
            <p>
              Text with <a href="#" className="text-blue-600 hover:underline">link</a>, 
              <strong>bold</strong>, and <em>italic</em>.
            </p>
          </CardContent>
        </Card>

        {/* Test Section: Colors */}
        <Card>
          <CardHeader>
            <CardTitle>Colors</CardTitle>
          </CardHeader>
          <CardContent>
            <div className="grid grid-cols-2 md:grid-cols-4 gap-4">
              <div className="flex flex-col items-center">
                <div className="w-16 h-16 rounded bg-primary"></div>
                <p className="mt-2 text-xs">Primary</p>
              </div>
              <div className="flex flex-col items-center">
                <div className="w-16 h-16 rounded bg-secondary"></div>
                <p className="mt-2 text-xs">Secondary</p>
              </div>
              <div className="flex flex-col items-center">
                <div className="w-16 h-16 rounded bg-accent"></div>
                <p className="mt-2 text-xs">Accent</p>
              </div>
              <div className="flex flex-col items-center">
                <div className="w-16 h-16 rounded bg-muted"></div>
                <p className="mt-2 text-xs">Muted</p>
              </div>
            </div>
          </CardContent>
        </Card>

        {/* Test Section: Buttons */}
        <Card>
          <CardHeader>
            <CardTitle>Buttons</CardTitle>
          </CardHeader>
          <CardContent>
            <div className="grid grid-cols-1 md:grid-cols-3 gap-4">
              <div>
                <h4 className="text-sm font-medium mb-2">Default</h4>
                <div className="flex flex-wrap gap-2">
                  <Button variant="default">Default</Button>
                  <Button variant="default" className="btn-scale">With Scale</Button>
                </div>
              </div>
              <div>
                <h4 className="text-sm font-medium mb-2">Other Variants</h4>
                <div className="flex flex-wrap gap-2">
                  <Button variant="destructive">Destructive</Button>
                  <Button variant="outline">Outline</Button>
                  <Button variant="ghost">Ghost</Button>
                </div>
              </div>
              <div>
                <h4 className="text-sm font-medium mb-2">Sizes</h4>
                <div className="flex flex-wrap gap-2">
                  <Button size="sm">Small</Button>
                  <Button size="default">Default</Button>
                  <Button size="lg">Large</Button>
                </div>
              </div>
            </div>
          </CardContent>
        </Card>

        {/* Test Section: Cards */}
        <Card>
          <CardHeader>
            <CardTitle>Cards</CardTitle>
          </CardHeader>
          <CardContent>
            <div className="grid grid-cols-1 md:grid-cols-3 gap-4">
              <Card className="overflow-hidden border-t-4 border-t-primary hover-card">
                <CardHeader>
                  <CardTitle className="text-sm">Border Top Primary</CardTitle>
                </CardHeader>
                <CardContent>
                  <p className="text-sm">Card with hover effect</p>
                </CardContent>
              </Card>
              <Card className="overflow-hidden border-t-4 border-t-accent hover-card">
                <CardHeader>
                  <CardTitle className="text-sm">Border Top Accent</CardTitle>
                </CardHeader>
                <CardContent>
                  <p className="text-sm">Card with hover effect</p>
                </CardContent>
              </Card>
              <Card className="shadow-md transition-all hover:border-primary">
                <CardHeader>
                  <CardTitle className="text-sm">Shadow Card</CardTitle>
                </CardHeader>
                <CardContent>
                  <p className="text-sm">Card with hover border</p>
                </CardContent>
              </Card>
            </div>
          </CardContent>
        </Card>

        {/* Test Section: Animations */}
        <Card>
          <CardHeader>
            <CardTitle>Animations</CardTitle>
          </CardHeader>
          <CardContent>
            <div className="grid grid-cols-1 md:grid-cols-3 gap-4">
              <Card className="border border-border p-4">
                <div className="fade-in">Fade In Text</div>
              </Card>
              <Card className="border border-border p-4">
                <div className="spinner mx-auto"></div>
              </Card>
              <Card className="border border-border p-4">
                <Button className="btn-scale w-full">Scale on Hover</Button>
              </Card>
            </div>
          </CardContent>
        </Card>
      </div>

      {showDebugger && <StyleDebugger />}
    </div>
  );
}
