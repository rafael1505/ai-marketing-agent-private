"use client";

import React from "react";
import { Navbar } from "./navbar";
import { AppController } from "@/components/app-controller";
import { PageTransition } from "@/components/ui/page-transition";
import { ErrorBoundaryWithContext } from "@/components/error-boundary-with-context";
import { withAuthProvider } from "@/components/hoc/with-auth-provider";
import "./main-layout.css"; // Import the CSS file

interface LayoutProps {
  children: React.ReactNode;
  locale?: string;
}

export const MainLayout: React.FC<LayoutProps> = withAuthProvider(({ 
  children,
  locale = "en"
}) => {
  // Track if component has mounted on client
  const [isMounted, setIsMounted] = React.useState(false);
  
  // Simple client-side detection
  React.useEffect(() => {
    setIsMounted(true);
  }, []);
  
  return (
    <div className="flex flex-col min-h-screen bg-background text-foreground">
      <AppController />
      <Navbar locale={locale} />
      <main id="main-content" className="flex-grow flex flex-col items-center justify-center p-4 md:p-6 lg:p-8">
        <ErrorBoundaryWithContext>
          <PageTransition>
            {children}
          </PageTransition>
        </ErrorBoundaryWithContext>
      </main>
    </div>
  );
});
