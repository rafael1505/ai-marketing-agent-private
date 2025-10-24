/**
 * AI Provider Error Display Component
 * Shows user-friendly error messages with actionable guidance
 */
import React from "react";
import { Alert, AlertDescription } from "@/components/ui/alert";
import { Button } from "@/components/ui/button";
import { Card, CardContent, CardHeader, CardTitle } from "@/components/ui/card";
import { Badge } from "@/components/ui/badge";

interface AIErrorDetails {
  error_type: string;
  message: string;
  user_message: string;
  provider: string;
  correlation_id: string;
  timestamp: string;
  http_status?: number;
  suggested_actions: string[];
  details?: Record<string, any>;
  retry_after?: number;
}

interface AIErrorDisplayProps {
  error: string;
  errorDetails?: AIErrorDetails;
  onRetry?: () => void;
  onSwitchProvider?: () => void;
  locale?: string;
  translations?: Record<string, any>;
}

export const AIErrorDisplay: React.FC<AIErrorDisplayProps> = ({
  error,
  errorDetails,
  onRetry,
  onSwitchProvider,
  locale = "en",
  translations = {}
}) => {
  if (!errorDetails) {
    // Fallback for simple errors
    return (
      <Alert variant="destructive" className="my-4">
        <AlertDescription>{error}</AlertDescription>
      </Alert>
    );
  }

  const t = translations;
  const providerName = errorDetails.provider || "AI Provider";
  
  // Get translated error message
  const errorMessageKey = errorDetails.user_message || "errors.ai.unknown_error";
  const errorMessage = getNestedTranslation(t, errorMessageKey, { provider: providerName });
  
  // Get severity color
  const getSeverityColor = () => {
    switch (errorDetails.error_type) {
      case "billing_limit_reached":
      case "quota_exceeded":
        return "bg-amber-50 border-amber-200 dark:bg-amber-950 dark:border-amber-800";
      case "invalid_api_key":
      case "provider_not_configured":
        return "bg-red-50 border-red-200 dark:bg-red-950 dark:border-red-800";
      case "rate_limit_exceeded":
        return "bg-blue-50 border-blue-200 dark:bg-blue-950 dark:border-blue-800";
      case "content_policy_violation":
        return "bg-purple-50 border-purple-200 dark:bg-purple-950 dark:border-purple-800";
      case "network_error":
      case "timeout":
        return "bg-gray-50 border-gray-200 dark:bg-gray-950 dark:border-gray-800";
      default:
        return "bg-red-50 border-red-200 dark:bg-red-950 dark:border-red-800";
    }
  };

  // Get icon for error type
  const getErrorIcon = () => {
    const iconMap: Record<string, string> = {
      billing_limit_reached: "💳",
      invalid_api_key: "🔑",
      quota_exceeded: "📊",
      rate_limit_exceeded: "⏱️",
      content_policy_violation: "⚠️",
      network_error: "🌐",
      service_unavailable: "🔧",
      invalid_request: "❌",
      provider_not_configured: "⚙️",
      timeout: "⏰",
      unknown_error: "⚠️"
    };
    return iconMap[errorDetails.error_type] || "⚠️";
  };

  // Get provider-specific dashboard link
  const getProviderDashboard = () => {
    const dashboards: Record<string, string> = {
      openai: "https://platform.openai.com/account/billing",
      stability: "https://platform.stability.ai/account",
      replicate: "https://replicate.com/account",
      anthropic: "https://console.anthropic.com/settings/billing",
      huggingface: "https://huggingface.co/settings/billing"
    };
    return dashboards[errorDetails.provider.toLowerCase()];
  };

  return (
    <Card className={`my-4 ${getSeverityColor()}`}>
      <CardHeader className="pb-3">
        <div className="flex items-start justify-between">
          <div className="flex items-center gap-2">
            <span className="text-2xl">{getErrorIcon()}</span>
            <div>
              <CardTitle className="text-lg font-semibold">
                {errorMessage}
              </CardTitle>
              <p className="text-sm text-muted-foreground mt-1">
                {providerName}
              </p>
            </div>
          </div>
          <Badge variant="outline" className="text-xs">
            {errorDetails.error_type.replace(/_/g, " ").toUpperCase()}
          </Badge>
        </div>
      </CardHeader>
      
      <CardContent className="space-y-4">
        {/* Technical details (collapsed by default) */}
        <details className="text-sm">
          <summary className="cursor-pointer text-muted-foreground hover:text-foreground">
            Technical Details
          </summary>
          <div className="mt-2 p-3 bg-muted/50 rounded-md space-y-1">
            <p><strong>Correlation ID:</strong> <code className="text-xs">{errorDetails.correlation_id}</code></p>
            <p><strong>Timestamp:</strong> {new Date(errorDetails.timestamp).toLocaleString()}</p>
            {errorDetails.http_status && (
              <p><strong>HTTP Status:</strong> {errorDetails.http_status}</p>
            )}
            <p><strong>Message:</strong> {errorDetails.message}</p>
          </div>
        </details>

        {/* Suggested Actions */}
        {errorDetails.suggested_actions && errorDetails.suggested_actions.length > 0 && (
          <div className="space-y-2">
            <p className="font-semibold text-sm">
              {locale === "pt" ? "Ações Sugeridas:" : "Suggested Actions:"}
            </p>
            <ul className="space-y-2">
              {errorDetails.suggested_actions.map((actionKey, index) => {
                const actionText = getNestedTranslation(t, actionKey, {
                  correlationId: errorDetails.correlation_id,
                  seconds: errorDetails.retry_after || 60
                });
                return (
                  <li key={index} className="flex items-start gap-2 text-sm">
                    <span className="text-primary mt-0.5">→</span>
                    <span>{actionText}</span>
                  </li>
                );
              })}
            </ul>
          </div>
        )}

        {/* Action Buttons */}
        <div className="flex gap-2 flex-wrap pt-2">
          {onRetry && errorDetails.error_type !== "invalid_api_key" && (
            <Button
              onClick={onRetry}
              variant="default"
              size="sm"
              disabled={!!errorDetails.retry_after}
            >
              {errorDetails.retry_after 
                ? `${locale === "pt" ? "Aguarde" : "Wait"} ${errorDetails.retry_after}s`
                : locale === "pt" ? "Tentar Novamente" : "Try Again"
              }
            </Button>
          )}
          
          {onSwitchProvider && (
            <Button
              onClick={onSwitchProvider}
              variant="outline"
              size="sm"
            >
              {locale === "pt" ? "Trocar Provedor" : "Switch Provider"}
            </Button>
          )}
          
          {(errorDetails.error_type === "billing_limit_reached" || 
            errorDetails.error_type === "quota_exceeded" ||
            errorDetails.error_type === "invalid_api_key") && getProviderDashboard() && (
            <Button
              onClick={() => window.open(getProviderDashboard(), "_blank")}
              variant="outline"
              size="sm"
            >
              {locale === "pt" ? "Abrir Painel do Provedor" : "Open Provider Dashboard"} ↗
            </Button>
          )}
        </div>
      </CardContent>
    </Card>
  );
};

/**
 * Helper function to get nested translation value
 */
function getNestedTranslation(
  translations: Record<string, any>,
  key: string,
  replacements: Record<string, string | number> = {}
): string {
  const keys = key.split(".");
  let value: any = translations;
  
  for (const k of keys) {
    if (value && typeof value === "object" && k in value) {
      value = value[k];
    } else {
      return key; // Return key if translation not found
    }
  }
  
  // Replace placeholders
  if (typeof value === "string") {
    return value.replace(/\{\{(\w+)\}\}/g, (_, placeholder) => {
      return String(replacements[placeholder] || `{{${placeholder}}}`);
    });
  }
  
  return key;
}
