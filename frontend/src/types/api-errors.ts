/**
 * API error types mirroring the MCP contract (docs/mcp-connector-contract.md §3.2, §3.3).
 * Single source of truth for error payloads consumed by the API client and error display.
 */

/** Canonical error_type values from MCP contract §3.3. Extend with namespaced "<provider>.<reason>" if needed. */
export type ErrorType =
  | 'provider_unavailable'
  | 'provider_not_configured'
  | 'provider_not_found'
  | 'invalid_api_key'
  | 'quota_exceeded'
  | 'rate_limit_exceeded'
  | 'content_policy_violation'
  | 'invalid_request'
  | 'timeout'
  | 'service_error'
  | 'unknown_error'
  | 'network_error'; // client-side when no response

/**
 * Backend canonical error_details shape (MCP §3.2).
 * Required: error_type, user_message, provider, correlation_id, http_status.
 * Optional: details. Client-only fields (suggested_actions, timestamp) are added by the
 * normalizer for display and are optional when extending this interface.
 */
export interface ErrorDetails {
  error_type: string;
  user_message: string;
  provider: string;
  correlation_id: string;
  http_status: number;
  details?: Record<string, unknown>;
  /** Client-only: added by normalizer for display. */
  suggested_actions?: string[];
  /** Client-only: added by normalizer for display. */
  timestamp?: string;
}

/**
 * API response shape when the request failed and the backend returned error_details.
 * Use for typing response.data or error payloads.
 */
export interface ApiErrorPayload {
  success: false;
  error_details: ErrorDetails;
}

/**
 * Type guard: check if a value has the shape of ErrorDetails (at least required fields).
 */
export function isErrorDetails(value: unknown): value is ErrorDetails {
  if (!value || typeof value !== 'object') return false;
  const o = value as Record<string, unknown>;
  return (
    typeof o.error_type === 'string' &&
    typeof o.user_message === 'string' &&
    typeof o.provider === 'string' &&
    typeof o.correlation_id === 'string' &&
    typeof o.http_status === 'number'
  );
}
