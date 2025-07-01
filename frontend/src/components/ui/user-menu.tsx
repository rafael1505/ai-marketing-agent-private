"use client";

import React, { useState, useRef, useEffect } from "react";
import { cn } from "@/lib/utils";
import { Button } from "@/components/ui/button";
import Link from "next/link";
import { markAllNotificationsAsRead } from "@/lib/notification-utils";

interface UserMenuProps {
  userName?: string;
  userEmail?: string;
  userAvatar?: string;
  locale: string;
  translations: any;
  onLogout: () => void;
  className?: string;
  notificationsCount?: number;
}

export const UserMenu: React.FC<UserMenuProps> = ({
  userName = "Test User",
  userEmail = "test@example.com", 
  userAvatar,
  locale,
  translations,
  onLogout,
  className,
  notificationsCount = 0
}) => {
  const [isOpen, setIsOpen] = useState(false);
  const dropdownRef = useRef<HTMLDivElement>(null);
  const buttonRef = useRef<HTMLButtonElement>(null);

  // Close dropdown when clicking outside
  useEffect(() => {
    const handleClickOutside = (event: MouseEvent) => {
      if (
        dropdownRef.current && 
        !dropdownRef.current.contains(event.target as Node) &&
        buttonRef.current &&
        !buttonRef.current.contains(event.target as Node)
      ) {
        setIsOpen(false);
      }
    };

    document.addEventListener("mousedown", handleClickOutside);
    return () => {
      document.removeEventListener("mousedown", handleClickOutside);
    };
  }, []);

  // Close dropdown when pressing escape
  useEffect(() => {
    const handleEscape = (event: KeyboardEvent) => {
      if (event.key === "Escape") {
        setIsOpen(false);
      }
    };

    document.addEventListener("keydown", handleEscape);
    return () => {
      document.removeEventListener("keydown", handleEscape);
    };
  }, []);

  const handleToggle = () => {
    setIsOpen(!isOpen);
  };

  const handleLogout = () => {
    setIsOpen(false);
    onLogout();
  };
  
  const handleNotificationClick = async () => {
    setIsOpen(false);
    // When navigating to notifications, we'll mark them as read
    // This is just a demo - in a real app you'd want to confirm navigation success first
    try {
      await markAllNotificationsAsRead();
    } catch (error) {
      console.error("Failed to mark notifications as read:", error);
    }
  };

  const getInitials = (name: string) => {
    return name
      .split(" ")
      .map(part => part.charAt(0))
      .join("")
      .toUpperCase()
      .slice(0, 2);
  };

  const menuItems = [
    {
      label: translations.user_menu?.profile || "My Profile",
      icon: (
        <svg className="w-4 h-4" fill="none" stroke="currentColor" viewBox="0 0 24 24">
          <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M16 7a4 4 0 11-8 0 4 4 0 018 0zM12 14a7 7 0 00-7 7h14a7 7 0 00-7-7z" />
        </svg>
      ),
      href: `/${locale}/profile`,
      action: null
    },
    {
      label: translations.user_menu?.account_settings || "Account Settings",
      icon: (
        <svg className="w-4 h-4" fill="none" stroke="currentColor" viewBox="0 0 24 24">
          <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M10.325 4.317c.426-1.756 2.924-1.756 3.35 0a1.724 1.724 0 002.573 1.066c1.543-.94 3.31.826 2.37 2.37a1.724 1.724 0 001.065 2.572c1.756.426 1.756 2.924 0 3.35a1.724 1.724 0 00-1.066 2.573c.94 1.543-.826 3.31-2.37 2.37a1.724 1.724 0 00-2.572 1.065c-.426 1.756-2.924 1.756-3.35 0a1.724 1.724 0 00-2.573-1.066c-1.543.94-3.31-.826-2.37-2.37a1.724 1.724 0 00-1.065-2.572c-1.756-.426-1.756-2.924 0-3.35a1.724 1.724 0 001.066-2.573c-.94-1.543.826-3.31 2.37-2.37.996.608 2.296.07 2.572-1.065z" />
          <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M15 12a3 3 0 11-6 0 3 3 0 016 0z" />
        </svg>
      ),
      href: `/${locale}/settings`,
      action: null
    },
    {
      label: translations.user_menu?.notifications || "Notifications",
      icon: (
        <svg className="w-4 h-4" fill="none" stroke="currentColor" viewBox="0 0 24 24">
          <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M15 17h5l-5 5v-5zM4.5 19.5l15-15m0 0H8m11.5 0v11.5" />
          <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M18 8A6 6 0 006 8c0 7-3 9-3 9h18s-3-2-3-9" />
          <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M13.73 21a2 2 0 01-3.46 0" />
        </svg>
      ),
      href: `/${locale}/notifications`,
      action: null
    },
    {
      label: translations.user_menu?.preferences || "Preferences",
      icon: (
        <svg className="w-4 h-4" fill="none" stroke="currentColor" viewBox="0 0 24 24">
          <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M12 6V4m0 2a2 2 0 100 4m0-4a2 2 0 110 4m-6 8a2 2 0 100-4m0 4a2 2 0 100 4m0-4v2m0-6V4m6 6v10m6-2a2 2 0 100-4m0 4a2 2 0 100 4m0-4v2m0-6V4" />
        </svg>
      ),
      href: `/${locale}/preferences`,
      action: null
    },
    {
      label: translations.user_menu?.help_support || "Help & Support",
      icon: (
        <svg className="w-4 h-4" fill="none" stroke="currentColor" viewBox="0 0 24 24">
          <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M8.228 9c.549-1.165 2.03-2 3.772-2 2.21 0 4 1.343 4 3 0 1.4-1.278 2.575-3.006 2.907-.542.104-.994.54-.994 1.093m0 3h.01M21 12a9 9 0 11-18 0 9 9 0 0118 0z" />
        </svg>
      ),
      href: `/${locale}/help`,
      action: null
    },
    // Separator item (divider)
    {
      label: "divider",
      icon: null,
      href: null,
      action: null,
      variant: "divider" as const
    },
    {
      label: translations.user_menu?.logout || translations.nav?.logout || "Logout",
      icon: (
        <svg className="w-4 h-4" fill="none" stroke="currentColor" viewBox="0 0 24 24">
          <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M17 16l4-4m0 0l-4-4m4 4H7m6 4v1a3 3 0 01-3 3H6a3 3 0 01-3-3V7a3 3 0 013-3h4a3 3 0 013 3v1" />
        </svg>
      ),
      href: null,
      action: handleLogout,
      variant: "destructive" as const
    }
  ];

  return (
    <div className={cn("relative", className)}>
      {/* User Avatar Button */}
      <Button
        ref={buttonRef}
        variant="ghost"
        size="sm"
        onClick={handleToggle}
        className={cn(
          "flex items-center space-x-2 px-3 py-2 hover:bg-secondary/80 transition-all duration-200",
          "focus:outline-none focus:ring-2 focus:ring-primary focus:ring-offset-2",
          "border border-transparent hover:border-border/30 rounded-full",
          "hover:scale-105 transform", // Add subtle grow effect on hover
          isOpen && "bg-secondary/60"
        )}
        aria-expanded={isOpen}
        aria-haspopup="true"
      >
        {/* Avatar with potential notification badge */}
        <div className="flex items-center space-x-2 relative">
          <div className="relative overflow-hidden rounded-full ring-2 ring-background">
            {userAvatar ? (
              <img
                src={userAvatar}
                alt={`${userName}'s avatar`}
                className="w-9 h-9 rounded-full object-cover border border-border shadow-sm transition-transform hover:scale-110 duration-300"
              />
            ) : (
              <div className="w-9 h-9 rounded-full bg-gradient-to-br from-primary to-primary-light text-primary-foreground flex items-center justify-center text-sm font-semibold shadow-sm">
                {getInitials(userName)}
              </div>
            )}
            
            {/* Notification Badge - Only show if there are notifications */}
            {notificationsCount > 0 && (
              <span className="absolute -top-1 -right-1 flex items-center justify-center w-4 h-4 bg-red-500 text-white text-xs rounded-full">
                {notificationsCount > 9 ? '9+' : notificationsCount}
              </span>
            )}
          </div>
          
          {/* User Name (hidden on mobile) */}
          <span className="hidden sm:block text-sm font-medium text-foreground">
            {userName}
          </span>
          
          {/* Chevron Icon */}
          <svg
            className={cn(
              "w-4 h-4 text-muted-foreground transition-transform duration-200",
              isOpen && "rotate-180"
            )}
            fill="none"
            stroke="currentColor"
            viewBox="0 0 24 24"
          >
            <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M19 9l-7 7-7-7" />
          </svg>
        </div>
      </Button>

      {/* Dropdown Menu */}
      {isOpen && (
        <div
          ref={dropdownRef}
          className={cn(
            "absolute right-0 mt-2 w-72 bg-background border border-border rounded-md shadow-xl z-50",
            "animate-in fade-in-5 slide-in-from-top-5 duration-300",
            "backdrop-blur-sm bg-background/95 supports-[backdrop-filter]:bg-background/80" // Glass effect
          )}
        >
          {/* Enhanced User Info Header */}
          <div className="relative px-4 py-4 border-b border-border bg-gradient-to-r from-blue-50/30 to-purple-50/30">
            <div className="flex items-center space-x-3">
              {userAvatar ? (
                <img
                  src={userAvatar}
                  alt={`${userName}'s avatar`}
                  className="w-12 h-12 rounded-full object-cover border border-border shadow-md"
                />
              ) : (
                <div className="w-12 h-12 rounded-full bg-gradient-to-br from-blue-500 to-purple-500 text-white flex items-center justify-center text-base font-semibold shadow-md">
                  {getInitials(userName)}
                </div>
              )}
              <div className="flex-1 min-w-0">
                <p className="text-sm font-medium text-foreground truncate">
                  {userName}
                </p>
                <p className="text-xs text-muted-foreground truncate">
                  {userEmail}
                </p>
                <div className="mt-1">
                  <Link 
                    href={`/${locale}/profile`}
                    onClick={() => setIsOpen(false)}
                    className="text-xs text-primary hover:underline"
                  >
                    View profile
                  </Link>
                </div>
              </div>
            </div>
          </div>

          {/* Menu Items with improved styling */}
          <div className="py-1">
            {menuItems.map((item, index) => (
              <div key={index}>
                {item.variant === "divider" ? (
                  <div className="h-px bg-border my-1 mx-4"></div>
                ) : item.href ? (
                  <Link 
                    href={item.href}
                    onClick={() => setIsOpen(false)}
                    className={cn(
                      "flex items-center space-x-3 px-4 py-3 text-sm text-foreground hover:bg-secondary/80 transition-colors",
                      "focus:outline-none focus:bg-secondary/80 hover:text-primary"
                    )}
                  >
                    <span className="text-muted-foreground">{item.icon}</span>
                    <span>{item.label}</span>
                    
                    {/* Special badge for notifications */}
                    {item.label === (translations.user_menu?.notifications || "Notifications") && notificationsCount > 0 && (
                      <span className="ml-auto inline-flex items-center justify-center px-2 py-1 text-xs font-bold leading-none text-red-100 bg-red-500 rounded-full">
                        {notificationsCount}
                      </span>
                    )}
                  </Link>
                ) : item.action ? (
                  <button
                    onClick={item.action}
                    className={cn(
                      "w-full flex items-center space-x-3 px-4 py-3 text-sm transition-colors",
                      "focus:outline-none focus:bg-secondary/80",
                      item.variant === "destructive" 
                        ? "text-destructive hover:bg-destructive/10 hover:text-destructive" 
                        : "text-foreground hover:bg-secondary/80 hover:text-primary"
                    )}
                  >
                    <span className={cn(
                      item.variant === "destructive" ? "text-destructive" : "text-muted-foreground"
                    )}>
                      {item.icon}
                    </span>
                    <span>{item.label}</span>
                  </button>
                ) : null}
              </div>
            ))}
          </div>
          
          {/* Quick actions footer */}
          <div className="px-4 py-3 border-t border-border bg-secondary/20">
            <div className="flex items-center justify-between">
              <Link 
                href={`/${locale}/settings`}
                onClick={() => setIsOpen(false)}
                className="text-xs text-muted-foreground hover:text-primary"
              >
                Settings
              </Link>
              <Link 
                href={`/${locale}/help`}
                onClick={() => setIsOpen(false)}
                className="text-xs text-muted-foreground hover:text-primary"
              >
                Help
              </Link>
              <button
                onClick={handleLogout}
                className="text-xs text-destructive hover:text-destructive/80"
              >
                Logout
              </button>
            </div>
          </div>
        </div>
      )}
    </div>
  );
};
