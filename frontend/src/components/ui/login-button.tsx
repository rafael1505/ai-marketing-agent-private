"use client";

import React from "react";
import { cn } from "@/lib/utils";

interface LoginButtonProps extends React.ButtonHTMLAttributes<HTMLButtonElement> {
  isLoading?: boolean;
  children: React.ReactNode;
}

export const LoginButton: React.FC<LoginButtonProps> = ({
  className,
  isLoading = false,
  disabled,
  children,
  ...props
}) => {
  return (
    <button
      className={cn(
        "w-full flex items-center justify-center rounded-md bg-blue-500 hover:bg-blue-600 py-4 px-6",
        "text-white font-bold text-lg shadow-lg transition-all duration-200",
        "focus:outline-none focus:ring-2 focus:ring-blue-300 focus:ring-offset-2",
        "disabled:opacity-50 disabled:pointer-events-none",
        className
      )}
      style={{ color: 'white' }}
      disabled={disabled || isLoading}
      {...props}
    >
      {children}
    </button>
  );
};
