import React from "react";
// Temporarily disabled framer-motion to fix build issues
// import { AnimatePresence, motion } from "framer-motion";
import { Loader } from "./loader";

interface LoadingOverlayProps {
  isLoading: boolean;
  message?: string;
  fullScreen?: boolean;
}

export function LoadingOverlay({ 
  isLoading, 
  message = "Loading...", 
  fullScreen = false 
}: LoadingOverlayProps) {
  if (!isLoading) return null;
  
  return (
    <div
      className={`
        flex flex-col items-center justify-center bg-background/80 backdrop-blur-sm z-50
        ${fullScreen ? 'fixed inset-0' : 'absolute inset-0'}
      `}
    >
      <div className="flex flex-col items-center gap-4">
        <Loader size="lg" color="primary" />
        <p className="text-primary font-medium">{message}</p>
      </div>
    </div>
  );
}
