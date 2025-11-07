"""
AI Provider Error Classification System
Provides standardized error handling with correlation IDs, user-friendly messages, and actionable guidance.
"""
from enum import Enum
from typing import Optional, List, Dict, Any
from dataclasses import dataclass, field
import uuid
from datetime import datetime


class AIErrorType(Enum):
    """Standardized error types for AI provider operations"""
    BILLING_LIMIT_REACHED = "billing_limit_reached"
    INVALID_API_KEY = "invalid_api_key"
    QUOTA_EXCEEDED = "quota_exceeded"
    RATE_LIMIT_EXCEEDED = "rate_limit_exceeded"
    CONTENT_POLICY_VIOLATION = "content_policy_violation"
    NETWORK_ERROR = "network_error"
    SERVICE_UNAVAILABLE = "service_unavailable"
    INVALID_REQUEST = "invalid_request"
    PROVIDER_NOT_CONFIGURED = "provider_not_configured"
    TIMEOUT = "timeout"
    UNKNOWN_ERROR = "unknown_error"


@dataclass
class AIProviderError:
    """
    Enriched error object for AI provider operations
    
    Attributes:
        error_type: Standardized error classification
        message: Technical error message
        user_message: User-friendly error message (i18n key)
        provider: AI provider that raised the error
        correlation_id: Unique identifier for tracking/debugging
        timestamp: When the error occurred
        http_status: HTTP status code if applicable
        suggested_actions: List of i18n keys for suggested user actions
        details: Additional context (API response, error codes, etc.)
        retry_after: Seconds to wait before retry (for rate limits)
    """
    error_type: AIErrorType
    message: str
    user_message: str  # i18n key like 'errors.ai.billing_limit_reached'
    provider: str
    correlation_id: str = field(default_factory=lambda: str(uuid.uuid4()))
    timestamp: str = field(default_factory=lambda: datetime.utcnow().isoformat())
    http_status: Optional[int] = None
    suggested_actions: List[str] = field(default_factory=list)  # i18n keys
    details: Dict[str, Any] = field(default_factory=dict)
    retry_after: Optional[int] = None

    def to_dict(self) -> Dict[str, Any]:
        """Convert error to dictionary for API response"""
        return {
            "error_type": self.error_type.value,
            "message": self.message,
            "user_message": self.user_message,
            "provider": self.provider,
            "correlation_id": self.correlation_id,
            "timestamp": self.timestamp,
            "http_status": self.http_status,
            "suggested_actions": self.suggested_actions,
            "details": self.details,
            "retry_after": self.retry_after
        }


class AIErrorClassifier:
    """Classifies provider-specific errors into standardized error types"""
    
    @staticmethod
    def classify_openai_error(status_code: int, error_data: Dict[str, Any]) -> tuple[AIErrorType, str, List[str]]:
        """
        Classify OpenAI API errors
        
        Returns:
            (error_type, user_message_key, suggested_actions_keys)
        """
        error_message = error_data.get("error", {}).get("message", "")
        error_code = error_data.get("error", {}).get("code", "")
        error_type_str = error_data.get("error", {}).get("type", "")
        
        # Billing and quota errors
        if status_code == 429:
            if "quota" in error_message.lower() or "insufficient_quota" in error_code:
                return (
                    AIErrorType.QUOTA_EXCEEDED,
                    "errors.ai.quota_exceeded",
                    ["actions.check_billing", "actions.upgrade_plan", "actions.switch_provider"]
                )
            return (
                AIErrorType.RATE_LIMIT_EXCEEDED,
                "errors.ai.rate_limit_exceeded",
                ["actions.wait_and_retry", "actions.reduce_frequency"]
            )
        
        # Authentication errors
        if status_code == 401 or "invalid_api_key" in error_code:
            return (
                AIErrorType.INVALID_API_KEY,
                "errors.ai.invalid_api_key",
                ["actions.check_api_key", "actions.regenerate_key", "actions.configure_provider"]
            )
        
        # Content policy violations
        if status_code == 400 and ("content_policy" in error_message.lower() or "safety_system" in error_message.lower()):
            return (
                AIErrorType.CONTENT_POLICY_VIOLATION,
                "errors.ai.content_policy_violation",
                ["actions.modify_prompt", "actions.review_guidelines"]
            )
        
        # Invalid request
        if status_code == 400:
            return (
                AIErrorType.INVALID_REQUEST,
                "errors.ai.invalid_request",
                ["actions.check_parameters", "actions.review_docs"]
            )
        
        # Service errors
        if status_code >= 500:
            return (
                AIErrorType.SERVICE_UNAVAILABLE,
                "errors.ai.service_unavailable",
                ["actions.try_again_later", "actions.switch_provider", "actions.check_status"]
            )
        
        return (
            AIErrorType.UNKNOWN_ERROR,
            "errors.ai.unknown_error",
            ["actions.contact_support", "actions.check_logs"]
        )
    
    @staticmethod
    def classify_stability_error(status_code: int, error_data: Dict[str, Any]) -> tuple[AIErrorType, str, List[str]]:
        """Classify Stability AI errors"""
        message = error_data.get("message", "").lower()
        
        if status_code == 402:
            return (
                AIErrorType.BILLING_LIMIT_REACHED,
                "errors.ai.billing_limit_reached",
                ["actions.add_payment_method", "actions.check_billing", "actions.switch_provider"]
            )
        
        if status_code == 401:
            return (
                AIErrorType.INVALID_API_KEY,
                "errors.ai.invalid_api_key",
                ["actions.check_api_key", "actions.configure_provider"]
            )
        
        if status_code == 429:
            return (
                AIErrorType.RATE_LIMIT_EXCEEDED,
                "errors.ai.rate_limit_exceeded",
                ["actions.wait_and_retry", "actions.upgrade_plan"]
            )
        
        if status_code >= 500:
            return (
                AIErrorType.SERVICE_UNAVAILABLE,
                "errors.ai.service_unavailable",
                ["actions.try_again_later", "actions.check_status"]
            )
        
        return (
            AIErrorType.UNKNOWN_ERROR,
            "errors.ai.unknown_error",
            ["actions.contact_support"]
        )
    
    @staticmethod
    def classify_network_error(exception: Exception) -> tuple[AIErrorType, str, List[str]]:
        """Classify network/connection errors"""
        error_str = str(exception).lower()
        
        if "timeout" in error_str:
            return (
                AIErrorType.TIMEOUT,
                "errors.ai.timeout",
                ["actions.try_again", "actions.check_connection"]
            )
        
        # SSL/connection errors (cannot connect to host, SSL errors, etc.)
        if any(keyword in error_str for keyword in ["cannot connect", "ssl", "connect call failed", "connection refused", "connection reset"]):
            return (
                AIErrorType.NETWORK_ERROR,
                "errors.ai.connection_failed",
                ["actions.check_internet", "actions.check_firewall", "actions.try_again", "actions.contact_support"]
            )
        
        if "connection" in error_str or "network" in error_str:
            return (
                AIErrorType.NETWORK_ERROR,
                "errors.ai.network_error",
                ["actions.check_connection", "actions.try_again"]
            )
        
        return (
            AIErrorType.UNKNOWN_ERROR,
            "errors.ai.unknown_error",
            ["actions.contact_support"]
        )
    
    @staticmethod
    def classify_provider_error(provider: str, status_code: Optional[int], error_data: Dict[str, Any], exception: Optional[Exception] = None) -> AIProviderError:
        """
        Main entry point for error classification
        
        Args:
            provider: Provider name (openai, stability, etc.)
            status_code: HTTP status code if applicable
            error_data: Error response data from provider
            exception: Python exception if applicable
        
        Returns:
            Enriched AIProviderError object
        """
        # Network/connection errors
        if exception and status_code is None:
            error_type, user_message, actions = AIErrorClassifier.classify_network_error(exception)
            return AIProviderError(
                error_type=error_type,
                message=str(exception),
                user_message=user_message,
                provider=provider,
                suggested_actions=actions,
                details={"exception_type": type(exception).__name__}
            )
        
        # Provider-specific classification
        if provider == "openai" and status_code:
            error_type, user_message, actions = AIErrorClassifier.classify_openai_error(status_code, error_data)
        elif provider == "stability" and status_code:
            error_type, user_message, actions = AIErrorClassifier.classify_stability_error(status_code, error_data)
        else:
            error_type = AIErrorType.UNKNOWN_ERROR
            user_message = "errors.ai.unknown_error"
            actions = ["actions.contact_support"]
        
        # Extract retry-after header for rate limits
        retry_after = None
        if error_type == AIErrorType.RATE_LIMIT_EXCEEDED:
            retry_after = error_data.get("retry_after", 60)
        
        return AIProviderError(
            error_type=error_type,
            message=error_data.get("error", {}).get("message", str(error_data)) if isinstance(error_data, dict) else str(error_data),
            user_message=user_message,
            provider=provider,
            http_status=status_code,
            suggested_actions=actions,
            details=error_data if isinstance(error_data, dict) else {"raw_error": str(error_data)},
            retry_after=retry_after
        )
