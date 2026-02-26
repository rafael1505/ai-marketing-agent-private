/**
 * AI Error Display (004 Phase 4 — T016, T017)
 * Primary: consumes errorDetails from useError(); shows user_message, Technical Details, Copy Support ID.
 * Optional: when errorDetails (and locale/translations) are passed as props, uses them for inline/page-level display.
 */
"use client";

import React, { useMemo, useCallback } from "react";
import { useError } from "@/contexts/error-context";
import type { ErrorDetails } from "@/contexts/error-context";
import { usePathname } from "@/i18n";
import { getTranslations } from "@/i18n";
import { Button } from "@/components/ui/button";
import { Card, CardContent, CardHeader, CardTitle } from "@/components/ui/card";

function getNestedTranslation(
  translations: Record<string, unknown>,
  key: string,
  replacements: Record<string, string | number> = {}
): string {
  const keys = key.split(".");
  let value: unknown = translations;
  for (const k of keys) {
    if (value && typeof value === "object" && k in (value as object)) {
      value = (value as Record<string, unknown>)[k];
    } else {
      return key;
    }
  }
  if (typeof value === "string") {
    return value.replace(/\{\{(\w+)\}\}/g, (_, placeholder) =>
      String(replacements[placeholder] ?? `{{${placeholder}}}`)
    );
  }
  return key;
}

/** Inline usage: pass errorDetails (and optionally locale, translations, onRetry). */
interface AIErrorDisplayProps {
  error?: string;
  errorDetails?: ErrorDetails | null;
  onRetry?: () => void;
  onSwitchProvider?: () => void;
  locale?: string;
  translations?: Record<string, unknown>;
}

export const AIErrorDisplay: React.FC<AIErrorDisplayProps> = ({
  error: propsError,
  errorDetails: propsErrorDetails,
  locale: propsLocale,
  translations: propsTranslations,
  onRetry,
}) => {
  const context = useError();
  const pathname = usePathname();
  const localeFromPath = (pathname?.split("/")[1] as "en" | "pt") || "en";
  const locale = propsLocale ?? localeFromPath;

  const t = useMemo(() => {
    if (propsTranslations && typeof propsTranslations === "object") return propsTranslations;
    return getTranslations(locale === "pt" ? "pt" : "en");
  }, [locale, propsTranslations]);

  const errorDetails = propsErrorDetails ?? context.errorDetails;
  const clearError = context.clearError;
  const isFromContext = propsErrorDetails == null;

  const handleCopySupportId = useCallback(() => {
    if (!errorDetails?.correlation_id) return;
    navigator.clipboard.writeText(errorDetails.correlation_id);
  }, [errorDetails?.correlation_id]);

  const handleDismiss = useCallback(() => {
    if (isFromContext) clearError();
    else onRetry?.();
  }, [isFromContext, clearError, onRetry]);

  if (!errorDetails) return null;

  const messageKey = errorDetails.user_message || (errorDetails as { message?: string }).message;
  const translated = messageKey
    ? getNestedTranslation(t, messageKey, { provider: errorDetails.provider || "AI Provider" })
    : "";
  const displayMessage =
    (translated && translated !== messageKey ? translated : null) ||
    (errorDetails as { message?: string }).message ||
    propsError ||
    "An error occurred";

  return (
    <Card className="my-4 bg-red-50 border-red-200 dark:bg-red-950 dark:border-red-800">
      <CardHeader className="pb-2">
        <div className="flex items-start justify-between gap-2">
          <CardTitle className="text-lg font-semibold">
            {displayMessage}
          </CardTitle>
          <Button variant="ghost" size="sm" onClick={handleDismiss} aria-label="Dismiss">
            ✕
          </Button>
        </div>
      </CardHeader>
      <CardContent className="space-y-3">
        <details className="text-sm">
          <summary className="cursor-pointer text-muted-foreground hover:text-foreground">
            Technical Details
          </summary>
          <div className="mt-2 p-3 bg-muted/50 rounded-md space-y-1">
            {errorDetails.correlation_id && (
              <p>
                <strong>Correlation ID:</strong>{" "}
                <code className="text-xs">{errorDetails.correlation_id}</code>
              </p>
            )}
            {errorDetails.error_type && (
              <p>
                <strong>Error type:</strong> {errorDetails.error_type.replace(/_/g, " ")}
              </p>
            )}
            {errorDetails.provider && (
              <p>
                <strong>Provider:</strong> {errorDetails.provider}
              </p>
            )}
            {errorDetails.timestamp && (
              <p>
                <strong>Timestamp:</strong>{" "}
                {new Date(errorDetails.timestamp).toLocaleString()}
              </p>
            )}
            {errorDetails.http_status != null && (
              <p>
                <strong>HTTP Status:</strong> {errorDetails.http_status}
              </p>
            )}
          </div>
        </details>
        {errorDetails.correlation_id && (
          <Button variant="outline" size="sm" onClick={handleCopySupportId}>
            Copy Support ID
          </Button>
        )}
      </CardContent>
    </Card>
  );
};
