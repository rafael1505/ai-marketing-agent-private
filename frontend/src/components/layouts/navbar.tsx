"use client";

import Link from "next/link";
import { getTranslations } from "@/i18n";
import { Button } from "@/components/ui/button";
import { UserMenu } from "@/components/ui/user-menu";
import { getUserDisplayName, getUserEmail, getUserAvatar, decodeJWTPayload } from "@/lib/user-utils";
import { getUnreadNotificationCount } from "@/lib/notification-utils";
import React from "react";
import { useAuth } from "@/contexts/auth-context";

interface NavbarProps {
  locale?: string;
}

export const Navbar: React.FC<NavbarProps> = ({ locale = "en" }) => {
  const t = getTranslations(locale === "pt" ? "pt" : "en");
  
  // Safe auth context access
  let authContext;
  try {
    authContext = useAuth();
  } catch (error) {
    console.warn('Navbar: useAuth failed, using fallback', error);
    authContext = {
      isLoggedIn: false,
      logout: () => {},
      token: null
    };
  }
  
  const { isLoggedIn, logout, token } = authContext;
  
  // Phase 1: Track if we're on the client
  const [isClient, setIsClient] = React.useState(false);
  
  // Phase 2: Only track auth state after client is confirmed
  const [authState, setAuthState] = React.useState({ isLoggedIn: false, hasToken: false });
  
  // Add notification count state for the user menu
  const [notificationsCount, setNotificationsCount] = React.useState(0);
  
  // First effect: Just set client flag
  React.useEffect(() => {
    setIsClient(true);
  }, []);
  
  // Second effect: Only update auth state after client is confirmed
  React.useEffect(() => {
    if (isClient) {
      setAuthState({ isLoggedIn, hasToken: !!token });
      console.log("Navbar auth state updated:", { isLoggedIn, hasToken: !!token, locale });
    }
  }, [isClient, isLoggedIn, token, locale]);

  const handleLogout = () => {
    console.log("Logout button clicked");
    logout(locale);
  };
  
  // For server render and initial client render, use a safe default that matches the server output
  // During server rendering, these will always be false since auth state only exists on client
  const shouldShowNavLinks = isClient ? (isLoggedIn || authState.isLoggedIn || !!token) : false;
  
  // Get user info for the UserMenu
  const userInfo = React.useMemo(() => {
    return token ? decodeJWTPayload(token) : null;
  }, [token]);
    // Fetch notifications count
  React.useEffect(() => {
    // Only fetch if the user is authenticated
    if (isClient && isLoggedIn && token) {
      // Fetch the notification count using our utility
      async function fetchNotificationCount() {
        try {
          const count = await getUnreadNotificationCount();
          setNotificationsCount(count);
        } catch (error) {
          console.error('Failed to fetch notification count:', error);
        }
      }
      
      // Initial fetch
      fetchNotificationCount();
      
      // Set up periodic refresh every 30 seconds
      const intervalId = setInterval(fetchNotificationCount, 30000);
      
      // Clean up interval on unmount
      return () => clearInterval(intervalId);
    }
  }, [isClient, isLoggedIn, token]);

  if (isClient) {
    console.log("Navbar client rendering with navigation links:", shouldShowNavLinks);
  }
  // Server-side rendering (and initial client render before hydration)
  // must match exactly or we'll get hydration errors
  const renderNavLinks = () => {
    // Only show nav links on client after we've confirmed auth state
    if (!isClient || !shouldShowNavLinks) {
      return null;
    }
    
    return (
      <>
        <Link
          href={`/${locale}/dashboard`}
          className="transition-all duration-200 hover:text-primary relative group"
        >
          <span>{t.nav.dashboard}</span>
          <span className="absolute bottom-0 left-0 w-0 h-0.5 bg-primary transition-all duration-300 group-hover:w-full"></span>
        </Link>
        <Link
          href={`/${locale}/materials`}
          className="transition-all duration-200 hover:text-primary relative group"
        >
          <span>{t.nav.materials}</span>
          <span className="absolute bottom-0 left-0 w-0 h-0.5 bg-primary transition-all duration-300 group-hover:w-full"></span>
        </Link>
        <Link
          href={`/${locale}/ai-providers`}
          className="transition-all duration-200 hover:text-primary relative group"
        >
          <span>AI Providers</span>
          <span className="absolute bottom-0 left-0 w-0 h-0.5 bg-primary transition-all duration-300 group-hover:w-full"></span>
        </Link>
        <Link
          href={`/${locale}/settings`}
          className="transition-all duration-200 hover:text-primary relative group"
        >
          <span>{t.nav.settings}</span>
          <span className="absolute bottom-0 left-0 w-0 h-0.5 bg-primary transition-all duration-300 group-hover:w-full"></span>
        </Link>
        <Link
          href={`/component-showcase`}
          className="transition-all duration-200 hover:text-accent relative group"
        >
          <span>UI Components</span>
          <span className="absolute bottom-0 left-0 w-0 h-0.5 bg-accent transition-all duration-300 group-hover:w-full"></span>
        </Link>
      </>
    );
  };

  return (
    <header className="sticky top-0 z-50 w-full border-b bg-background/95 backdrop-blur supports-[backdrop-filter]:bg-background/60 shadow-sm">
      <div className="container mx-auto flex h-16 items-center px-4 sm:px-6">
        <div className="mr-4 flex">
          <Link href="/" className="mr-8 flex items-center space-x-2 transition-opacity hover:opacity-80">
            <span className="font-bold text-xl gradient-text">{t.app.title}</span>
          </Link>
          <nav className="hidden md:flex items-center space-x-8 text-sm font-medium">
            {renderNavLinks()}
          </nav>
        </div>        <div className="ml-auto flex items-center space-x-4">
          <div className="flex items-center rounded-full bg-secondary/50 px-2 py-1">
            <Link
              href="/en"
              className={`px-2 transition-colors hover:text-primary ${locale === "en" ? "font-bold text-primary" : ""}`}
            >
              EN
            </Link>
            <div className="h-4 w-px bg-border/60"></div>
            <Link
              href="/pt"
              className={`px-2 transition-colors hover:text-primary ${locale === "pt" ? "font-bold text-primary" : ""}`}
            >
              PT
            </Link>          </div>          
            {/* We render login/logout buttons differently based on client state */}
          {isClient && shouldShowNavLinks ? (
            <UserMenu
              userName={getUserDisplayName(userInfo)}
              userEmail={getUserEmail(userInfo)}
              userAvatar={getUserAvatar(userInfo)}
              locale={locale}
              translations={t}
              onLogout={handleLogout}
              notificationsCount={notificationsCount}
              className="shadow-sm hover:shadow-md transition-shadow"
            />
          ) : (
            <Button
              variant="default"
              size="sm"
              asChild
              className="shadow-md"
            >
              <Link href={`/${locale}/login`}>
                {t.login.title}
              </Link>
            </Button>
          )}
        </div>
      </div>
    </header>
  );
};
