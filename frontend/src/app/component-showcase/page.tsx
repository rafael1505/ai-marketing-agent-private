"use client";

import React, { useState } from "react";
import { MainLayout } from "@/components/layouts/main-layout";
import { Card, CardContent, CardDescription, CardHeader, CardTitle } from "@/components/ui/card";
import { Button } from "@/components/ui/button";
import { Input } from "@/components/ui/input";
import { Label } from "@/components/ui/label";
import { Textarea } from "@/components/ui/textarea";
import { Loader } from "@/components/ui/loader";
import { LoadingOverlay } from "@/components/ui/loading-overlay";
import { FormSkeleton } from "@/components/ui/skeleton";
import Link from "next/link";

export default function ComponentShowcase() {
  const [isLoading, setIsLoading] = useState(false);
  const [showLoadingOverlay, setShowLoadingOverlay] = useState(false);

  const toggleLoading = () => {
    setIsLoading(prev => !prev);
    
    if (!isLoading) {
      setTimeout(() => {
        setIsLoading(false);
      }, 3000);
    }
  };

  const toggleLoadingOverlay = () => {
    setShowLoadingOverlay(prev => !prev);
    
    if (!showLoadingOverlay) {
      setTimeout(() => {
        setShowLoadingOverlay(false);
      }, 3000);
    }
  };

  return (
    <MainLayout>
      <div className="max-w-5xl mx-auto space-y-10">
        <div className="text-center mb-10">
          <h1 className="text-3xl font-bold gradient-text mb-2">Component Showcase</h1>
          <p className="text-muted-foreground">
            A visual reference of all styled UI components
          </p>
        </div>

        <div className="stagger-fade-in">
          {/* Typography Section */}
          <Card className="mb-8 hover-card shadow-md">
            <CardHeader className="bg-gradient-to-r from-primary/5 to-secondary/5">
              <CardTitle>Typography</CardTitle>
              <CardDescription>Text styles used throughout the application</CardDescription>
            </CardHeader>
            <CardContent className="space-y-6 pt-6">
              <h1 className="scroll-m-20 text-4xl font-extrabold tracking-tight lg:text-5xl mb-2">
                Heading Level 1
              </h1>
              <h2 className="scroll-m-20 text-3xl font-semibold tracking-tight mb-2">
                Heading Level 2
              </h2>
              <h3 className="scroll-m-20 text-2xl font-semibold tracking-tight mb-2">
                Heading Level 3
              </h3>
              <h4 className="scroll-m-20 text-xl font-semibold tracking-tight mb-2">
                Heading Level 4
              </h4>
              <p className="leading-7">
                This is a paragraph of text that should wrap onto multiple lines if it's long enough.
                We want to make sure that the text wraps correctly and has appropriate line height.
              </p>
              <p className="text-sm text-muted-foreground">
                This is smaller text meant for captions or secondary information.
              </p>
              <div>
                <p className="gradient-text text-xl font-semibold">Gradient Text</p>
              </div>
            </CardContent>
          </Card>

          {/* Buttons Section */}
          <Card className="mb-8 hover-card shadow-md">
            <CardHeader className="bg-gradient-to-r from-primary/5 to-secondary/5">
              <CardTitle>Buttons</CardTitle>
              <CardDescription>Various button styles and states</CardDescription>
            </CardHeader>
            <CardContent className="space-y-6 pt-6">
              <div className="flex flex-wrap gap-4">
                <Button variant="default" className="btn-scale">Primary Button</Button>
                <Button variant="outline" className="btn-scale">Secondary Button</Button>
                <Button variant="outline" className="btn-scale">Outline Button</Button>
                <Button variant="ghost" className="btn-scale">Ghost Button</Button>
                <Button variant="destructive" className="btn-scale">Destructive Button</Button>
                <Button variant="link">Link Button</Button>
              </div>
              <div className="flex flex-wrap gap-4">
                <Button disabled>Disabled Button</Button>
                <Button variant="outline" disabled>Disabled Outline</Button>
                <Button className="btn-scale gap-2">
                  <span className="spinner w-4 h-4"></span>
                  With Spinner
                </Button>
              </div>
              <div className="flex flex-wrap gap-4">
                <Button variant="default" size="sm" className="btn-scale">Small Button</Button>
                <Button variant="default" className="btn-scale">Default Button</Button>
                <Button variant="default" size="lg" className="btn-scale">Large Button</Button>
              </div>
            </CardContent>
          </Card>

          {/* Forms Section */}
          <Card className="mb-8 hover-card shadow-md">
            <CardHeader className="bg-gradient-to-r from-primary/5 to-secondary/5">
              <CardTitle>Form Controls</CardTitle>
              <CardDescription>Input fields and form elements</CardDescription>
            </CardHeader>
            <CardContent className="space-y-6 pt-6">
              <div className="space-y-2">
                <Label htmlFor="name">Name</Label>
                <Input id="name" placeholder="Enter your name" />
              </div>
              <div className="space-y-2">
                <Label htmlFor="email">Email</Label>
                <div className="relative">
                  <svg xmlns="http://www.w3.org/2000/svg" width="18" height="18" viewBox="0 0 24 24" fill="none" stroke="currentColor" strokeWidth="2" strokeLinecap="round" strokeLinejoin="round" className="absolute left-3 top-1/2 -translate-y-1/2 text-muted-foreground">
                    <path d="M22 17a2 2 0 0 1-2 2H4a2 2 0 0 1-2-2V9.5C2 7 4 5 6.5 5H18c2.2 0 4 1.8 4 4v8Z"/>
                    <polyline points="15,9 18,9 18,11"/>
                    <path d="M6 10V5c0-1.1.9-2 2-2h8a2 2 0 0 1 2 2v5"/>
                  </svg>
                  <Input id="email" placeholder="Enter your email" className="pl-10" />
                </div>
              </div>
              <div className="space-y-2">
                <Label htmlFor="message">Message</Label>
                <Textarea id="message" placeholder="Enter your message" rows={4} />
              </div>
              <div className="grid grid-cols-1 sm:grid-cols-2 gap-4">
                <div className="space-y-2">
                  <Label htmlFor="password">Password</Label>
                  <Input id="password" type="password" placeholder="Enter password" />
                </div>
                <div className="space-y-2">
                  <Label htmlFor="confirmPassword">Confirm Password</Label>
                  <Input id="confirmPassword" type="password" placeholder="Confirm password" />
                </div>
              </div>
              <div className="flex justify-end">
                <Button type="submit" className="btn-scale">Submit Form</Button>
              </div>
            </CardContent>
          </Card>

          {/* Loaders & Loading States */}
          <Card className="mb-8 hover-card shadow-md">
            <CardHeader className="bg-gradient-to-r from-primary/5 to-secondary/5">
              <CardTitle>Loaders & Loading States</CardTitle>
              <CardDescription>Different loading indicators and states</CardDescription>
            </CardHeader>
            <CardContent className="space-y-6 pt-6">
              <div className="flex flex-wrap gap-8">
                <div className="flex flex-col items-center space-y-2">
                  <Loader size="sm" />
                  <span className="text-sm">Small</span>
                </div>
                <div className="flex flex-col items-center space-y-2">
                  <Loader size="md" />
                  <span className="text-sm">Medium</span>
                </div>
                <div className="flex flex-col items-center space-y-2">
                  <Loader size="lg" />
                  <span className="text-sm">Large</span>
                </div>
              </div>
              <div className="space-y-4">
                <div className="rounded-md p-4 relative bg-muted/50">
                  {isLoading && (
                    <div className="absolute inset-0 flex items-center justify-center bg-background/80 backdrop-blur-sm rounded-md">
                      <Loader size="md" />
                    </div>
                  )}
                  <FormSkeleton />
                </div>
                <div className="flex space-x-4">
                  <Button onClick={toggleLoading} className="btn-scale">
                    {isLoading ? "Stop Loading" : "Show Section Loading"}
                  </Button>
                  <Button onClick={toggleLoadingOverlay} className="btn-scale" variant="outline">
                    {showLoadingOverlay ? "Stop Overlay" : "Show Loading Overlay"}
                  </Button>
                </div>
              </div>
            </CardContent>
          </Card>

          {/* Card & Container Styles */}
          <Card className="mb-8 hover-card shadow-md">
            <CardHeader className="bg-gradient-to-r from-primary/5 to-secondary/5">
              <CardTitle>Cards & Containers</CardTitle>
              <CardDescription>Different card styles and containers</CardDescription>
            </CardHeader>
            <CardContent className="space-y-6 pt-6">
              <div className="grid grid-cols-1 sm:grid-cols-3 gap-4">
                <Card className="border-t-4 border-t-primary">
                  <CardHeader className="bg-primary/5">
                    <CardTitle className="text-sm">Primary Card</CardTitle>
                  </CardHeader>
                  <CardContent className="pt-2 text-sm">
                    <p>This card has a primary color accent.</p>
                  </CardContent>
                </Card>
                
                <Card className="border-t-4 border-t-accent">
                  <CardHeader className="bg-accent/5">
                    <CardTitle className="text-sm">Accent Card</CardTitle>
                  </CardHeader>
                  <CardContent className="pt-2 text-sm">
                    <p>This card has an accent color accent.</p>
                  </CardContent>
                </Card>
                
                <Card className="border-t-4 border-t-success">
                  <CardHeader className="bg-success/5">
                    <CardTitle className="text-sm">Success Card</CardTitle>
                  </CardHeader>
                  <CardContent className="pt-2 text-sm">
                    <p>This card has a success color accent.</p>
                  </CardContent>
                </Card>
              </div>
              
              <div className="p-4 bg-secondary rounded-lg">
                <p>This is a secondary background container.</p>
              </div>
              
              <div className="p-4 bg-muted rounded-lg">
                <p>This is a muted background container.</p>
              </div>
            </CardContent>
          </Card>

          {/* Back to Dashboard Link */}
          <div className="text-center pt-8 pb-16">
            <Link href="/dashboard" className="text-primary hover:underline font-medium">
              Back to Dashboard
            </Link>
          </div>
        </div>
      </div>
      
      {/* Loading Overlay */}
      <LoadingOverlay isLoading={showLoadingOverlay} message="Loading Data..." />
    </MainLayout>
  );
}
