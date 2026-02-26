"use client";

import React, { createContext, useContext, useState, useCallback, ReactNode } from "react";

/**
 * Normalized error details for UI display and correlation traceability (004 frontend compliance).
 * At minimum: user_message and correlation_id; optional fields align with AIErrorDisplay.
 */
export interface ErrorDetails {
  user_message: string;
  correlation_id: string;
  error_type?: string;
  provider?: string;
  timestamp?: string;
  http_status?: number;
  message?: string;
  suggested_actions?: string[];
  details?: Record<string, unknown>;
  retry_after?: number;
}

interface ErrorContextType {
  /** Current error details, or null when no error. */
  errorDetails: ErrorDetails | null;
  /** Set error details (e.g. from API catch or error boundary). */
  setErrorDetails: (details: ErrorDetails | null) => void;
  /** Clear the current error. */
  clearError: () => void;
}

const ErrorContext = createContext<ErrorContextType | undefined>(undefined);

export { ErrorContext };

export const ErrorProvider: React.FC<{ children: ReactNode }> = ({ children }) => {
  const [errorDetails, setErrorDetailsState] = useState<ErrorDetails | null>(null);

  const setErrorDetails = useCallback((details: ErrorDetails | null) => {
    setErrorDetailsState(details);
  }, []);

  const clearError = useCallback(() => {
    setErrorDetailsState(null);
  }, []);

  const value: ErrorContextType = {
    errorDetails,
    setErrorDetails,
    clearError,
  };

  return (
    <ErrorContext.Provider value={value}>
      {children}
    </ErrorContext.Provider>
  );
};

export function useError(): ErrorContextType {
  const ctx = useContext(ErrorContext);
  if (ctx === undefined) {
    throw new Error("useError must be used within an ErrorProvider");
  }
  return ctx;
}
