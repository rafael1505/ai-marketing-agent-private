"use client";

import React, { Component, ErrorInfo, ReactNode } from "react";
import type { ErrorDetails } from "@/contexts/error-context";
import { Button } from "@/components/ui/button";
import { Card, CardContent, CardHeader, CardTitle } from "@/components/ui/card";

function generateCorrelationId(): string {
  if (typeof crypto !== "undefined" && typeof crypto.randomUUID === "function") {
    return crypto.randomUUID();
  }
  return `render-${Date.now()}-${Math.random().toString(36).slice(2, 11)}`;
}

interface ErrorBoundaryProps {
  children: ReactNode;
  setErrorDetails: (details: ErrorDetails | null) => void;
  clearError: () => void;
  fallback?: ReactNode;
}

interface ErrorBoundaryState {
  hasError: boolean;
  correlationId: string | null;
}

/**
 * React Error Boundary (004 T019, T020). Catches render errors and pushes
 * ErrorDetails into context so the UI can show user_message and correlation_id.
 */
export class ErrorBoundary extends Component<ErrorBoundaryProps, ErrorBoundaryState> {
  constructor(props: ErrorBoundaryProps) {
    super(props);
    this.state = { hasError: false, correlationId: null };
  }

  static getDerivedStateFromError(): Partial<ErrorBoundaryState> {
    return { hasError: true };
  }

  componentDidCatch(error: Error, errorInfo: ErrorInfo): void {
    const correlationId = generateCorrelationId();
    this.setState({ correlationId });
    const details: ErrorDetails = {
      user_message: "Something went wrong. Please try again.",
      correlation_id: correlationId,
      error_type: "render_error",
      message: error.message,
      timestamp: new Date().toISOString(),
    };
    this.props.setErrorDetails(details);
  }

  handleReset = (): void => {
    this.props.clearError();
    this.setState({ hasError: false, correlationId: null });
  };

  render(): ReactNode {
    if (this.state.hasError && this.state.correlationId) {
      if (this.props.fallback) return this.props.fallback;
      return (
        <Card className="my-4 border-amber-200 bg-amber-50 dark:border-amber-800 dark:bg-amber-950">
          <CardHeader>
            <CardTitle>Something went wrong</CardTitle>
          </CardHeader>
          <CardContent className="space-y-2">
            <p className="text-sm text-muted-foreground">
              Support ID: <code className="text-xs">{this.state.correlationId}</code>
            </p>
            <Button variant="outline" size="sm" onClick={this.handleReset}>
              Try again
            </Button>
          </CardContent>
        </Card>
      );
    }
    return this.props.children;
  }
}
