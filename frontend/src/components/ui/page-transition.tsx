"use client";

import React, { ReactNode } from "react";
// Temporarily disabled framer-motion to fix build issues
// import { motion, AnimatePresence } from "framer-motion";
import { usePathname } from "next/navigation";

interface PageTransitionProps {
  children: ReactNode;
}

export function PageTransition({ children }: PageTransitionProps) {
  const pathname = usePathname();
  
  return (
    <div key={pathname} className="w-full fade-in">
      {children}
    </div>
  );
}
