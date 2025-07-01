"use client";

import React, { useState, useEffect } from "react";
import { getTranslations } from "@/i18n";
import { Card, CardContent, CardDescription, CardHeader, CardTitle } from "@/components/ui/card";
import { Button } from "@/components/ui/button";
import { Badge } from "@/components/ui/badge";

export default function NotificationsPage({
  params
}: {
  params: { locale: string }
}) {
  const locale = params.locale || "en";
  const [t, setT] = useState<Record<string, any>>({});
  const [notifications, setNotifications] = useState([
    {
      id: 1,
      title: "Welcome to AI Marketing Agent",
      message: "Thank you for using our platform. Explore all the features available to you.",
      type: "info",
      read: false,
      timestamp: new Date(Date.now() - 2 * 60 * 60 * 1000) // 2 hours ago
    },
    {
      id: 2,
      title: "New Material Generated",
      message: "Your marketing material 'Product Launch Campaign' has been successfully generated.",
      type: "success",
      read: false,
      timestamp: new Date(Date.now() - 6 * 60 * 60 * 1000) // 6 hours ago
    },
    {
      id: 3,
      title: "Company Settings Updated",
      message: "Your company profile has been updated successfully.",
      type: "info",
      read: true,
      timestamp: new Date(Date.now() - 24 * 60 * 60 * 1000) // 1 day ago
    }
  ]);

  useEffect(() => {
    const loadTranslations = async () => {
      try {
        const translations = await getTranslations(locale === "pt" ? "pt" : "en");
        setT(translations);
      } catch (error) {
        console.error("Failed to load translations:", error);
        setT({});
      }
    };

    loadTranslations();
  }, [locale]);

  const markAsRead = (id: number) => {
    setNotifications(prev => 
      prev.map(notification => 
        notification.id === id 
          ? { ...notification, read: true }
          : notification
      )
    );
  };

  const markAllAsRead = () => {
    setNotifications(prev => 
      prev.map(notification => ({ ...notification, read: true }))
    );
  };

  const deleteNotification = (id: number) => {
    setNotifications(prev => prev.filter(notification => notification.id !== id));
  };

  const unreadCount = notifications.filter(n => !n.read).length;

  const getNotificationIcon = (type: string) => {
    switch (type) {
      case "success":
        return (
          <div className="w-10 h-10 rounded-full bg-green-100 flex items-center justify-center">
            <svg className="w-5 h-5 text-green-600" fill="none" stroke="currentColor" viewBox="0 0 24 24">
              <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M5 13l4 4L19 7" />
            </svg>
          </div>
        );
      case "warning":
        return (
          <div className="w-10 h-10 rounded-full bg-yellow-100 flex items-center justify-center">
            <svg className="w-5 h-5 text-yellow-600" fill="none" stroke="currentColor" viewBox="0 0 24 24">
              <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M12 9v2m0 4h.01m-6.938 4h13.856c1.54 0 2.502-1.667 1.732-2.5L13.732 4c-.77-.833-1.964-.833-2.732 0L3.268 16.5c-.77.833.192 2.5 1.732 2.5z" />
            </svg>
          </div>
        );
      case "error":
        return (
          <div className="w-10 h-10 rounded-full bg-red-100 flex items-center justify-center">
            <svg className="w-5 h-5 text-red-600" fill="none" stroke="currentColor" viewBox="0 0 24 24">
              <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M6 18L18 6M6 6l12 12" />
            </svg>
          </div>
        );
      default:
        return (
          <div className="w-10 h-10 rounded-full bg-blue-100 flex items-center justify-center">
            <svg className="w-5 h-5 text-blue-600" fill="none" stroke="currentColor" viewBox="0 0 24 24">
              <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M13 16h-1v-4h-1m1-4h.01M21 12a9 9 0 11-18 0 9 9 0 0118 0z" />
            </svg>
          </div>
        );
    }
  };

  const formatTimestamp = (timestamp: Date) => {
    const now = new Date();
    const diffInMinutes = Math.floor((now.getTime() - timestamp.getTime()) / (1000 * 60));
    
    if (diffInMinutes < 60) {
      return `${diffInMinutes} minutes ago`;
    } else if (diffInMinutes < 24 * 60) {
      const hours = Math.floor(diffInMinutes / 60);
      return `${hours} hour${hours > 1 ? 's' : ''} ago`;
    } else {
      const days = Math.floor(diffInMinutes / (24 * 60));
      return `${days} day${days > 1 ? 's' : ''} ago`;
    }
  };

  return (
    <div className="container mx-auto px-4 py-8 max-w-4xl">
      <div className="mb-8">
        <div className="flex items-center justify-between mb-4">
          <div>
            <h1 className="text-3xl font-bold text-foreground">
              {t.notifications?.title || "Notifications"}
            </h1>
            <p className="text-muted-foreground mt-2">
              {t.notifications?.description || "Stay updated with your latest activities and system updates"}
            </p>
          </div>
          
          <div className="flex items-center space-x-4">
            {unreadCount > 0 && (
              <Badge variant="secondary" className="px-3 py-1">
                {unreadCount} unread
              </Badge>
            )}
            {unreadCount > 0 && (
              <Button variant="outline" size="sm" onClick={markAllAsRead}>
                Mark all as read
              </Button>
            )}
          </div>
        </div>
      </div>

      <div className="space-y-4">
        {notifications.length === 0 ? (
          <Card>
            <CardContent className="text-center py-12">
              <svg className="w-16 h-16 text-muted-foreground mx-auto mb-4" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={1} d="M15 17h5l-5 5v-5zM4.5 19.5l15-15m0 0H8m11.5 0v11.5" />
                <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={1} d="M18 8A6 6 0 006 8c0 7-3 9-3 9h18s-3-2-3-9" />
              </svg>
              <h3 className="text-lg font-semibold text-foreground mb-2">
                {t.notifications?.no_notifications || "No notifications"}
              </h3>
              <p className="text-muted-foreground">
                {t.notifications?.no_notifications_description || "You're all caught up! No new notifications at this time."}
              </p>
            </CardContent>
          </Card>
        ) : (
          notifications.map((notification) => (
            <Card 
              key={notification.id} 
              className={`transition-colors ${!notification.read ? 'border-primary/20 bg-primary/5' : ''}`}
            >
              <CardContent className="p-6">
                <div className="flex items-start space-x-4">
                  {getNotificationIcon(notification.type)}
                  
                  <div className="flex-1 min-w-0">
                    <div className="flex items-start justify-between">
                      <div className="flex-1">
                        <h4 className={`text-sm font-semibold ${!notification.read ? 'text-foreground' : 'text-muted-foreground'}`}>
                          {notification.title}
                          {!notification.read && (
                            <Badge variant="secondary" className="ml-2 px-2 py-0.5 text-xs">
                              New
                            </Badge>
                          )}
                        </h4>
                        <p className="text-sm text-muted-foreground mt-1">
                          {notification.message}
                        </p>
                        <p className="text-xs text-muted-foreground mt-2">
                          {formatTimestamp(notification.timestamp)}
                        </p>
                      </div>
                      
                      <div className="flex items-center space-x-2 ml-4">
                        {!notification.read && (
                          <Button
                            variant="outline"
                            size="sm"
                            onClick={() => markAsRead(notification.id)}
                            className="text-xs"
                          >
                            Mark as read
                          </Button>
                        )}
                        <Button
                          variant="ghost"
                          size="sm"
                          onClick={() => deleteNotification(notification.id)}
                          className="text-xs text-muted-foreground hover:text-destructive"
                        >
                          Delete
                        </Button>
                      </div>
                    </div>
                  </div>
                </div>
              </CardContent>
            </Card>
          ))
        )}
      </div>
    </div>
  );
}
