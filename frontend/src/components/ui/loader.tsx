import React from "react";
import { cn } from "@/lib/utils";

interface LoaderProps {
  size?: "sm" | "md" | "lg";
  color?: "primary" | "accent" | "white";
  className?: string;
}

export function Loader({ size = "md", color = "primary", className }: LoaderProps) {
  const sizeClasses = {
    sm: "w-4 h-4 border-2",
    md: "w-6 h-6 border-2",
    lg: "w-8 h-8 border-3"
  };

  const colorClasses = {
    primary: "border-primary",
    accent: "border-accent",
    white: "border-white"
  };

  return (
    <div 
      className={cn(
        "spinner-container inline-flex items-center justify-center",
        className
      )}
    >
      <div 
        className={cn(
          "animate-spin rounded-full border-t-transparent",
          sizeClasses[size],
          `border-t-${color === 'primary' ? 'primary' : color === 'accent' ? 'accent' : 'white'}`
        )}
      />
    </div>
  );
}
