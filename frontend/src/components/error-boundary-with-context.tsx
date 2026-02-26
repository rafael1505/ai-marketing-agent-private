"use client";

import React, { ReactNode } from "react";
import { useError } from "@/contexts/error-context";
import { ErrorBoundary } from "@/components/error-boundary";
import { AIErrorDisplay } from "@/components/ui/ai-error-display";

interface Props {
  children: ReactNode;
}

/**
 * Wraps children with ErrorBoundary that pushes render errors into Error Context,
 * and renders the global AIErrorDisplay above content. Boundary fallback uses
 * the same AIErrorDisplay so render crashes are traceable via correlation_id.
 */
export function ErrorBoundaryWithContext({ children }: Props): React.ReactElement {
  const { setErrorDetails, clearError } = useError();
  return (
    <ErrorBoundary
      setErrorDetails={setErrorDetails}
      clearError={clearError}
      fallback={<AIErrorDisplay />}
    >
      <AIErrorDisplay />
      {children}
    </ErrorBoundary>
  );
}
