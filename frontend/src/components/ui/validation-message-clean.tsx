"use client";

import React from "react";
import { AlertCircle, Check, AlertTriangle } from "lucide-react";

interface ValidationMessageProps {
  type: "success" | "error" | "warning" | "info";
  message: string;
  className?: string;
}

export function ValidationMessage({ 
  type, 
  message, 
  className: additionalClassName 
}: ValidationMessageProps) {
  if (!message) return null;
  
  const getIconAndClass = () => {
    switch (type) {
      case "success":
        return {
          icon: <Check className="h-4 w-4" />,
          className: "bg-green-50 text-green-700 border-green-200"
        };
      case "error":
        return {
          icon: <AlertCircle className="h-4 w-4" />,
          className: "bg-red-50 text-red-700 border-red-200"
        };
      case "warning":
        return {
          icon: <AlertTriangle className="h-4 w-4" />,
          className: "bg-yellow-50 text-yellow-700 border-yellow-200"
        };
      case "info":
      default:
        return {
          icon: <AlertCircle className="h-4 w-4" />,
          className: "bg-blue-50 text-blue-700 border-blue-200"
        };
    }
  };
  
  const { icon, className } = getIconAndClass();
  
  return (
    <div 
      className={`flex items-center gap-2 text-sm p-2 rounded border ${className} ${
        additionalClassName || ""
      }`}
    >
      {icon}
      <span>{message}</span>
    </div>
  );
}
