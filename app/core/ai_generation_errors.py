"""
Enhanced error handling for AI image generation.
"""

from enum import Enum
from typing import Dict, Any, Optional, List
from dataclasses import dataclass
import logging
from datetime import datetime

logger = logging.getLogger(__name__)


class AIGenerationErrorType(Enum):
    """Classification of AI generation errors."""
    
    # API Key and Authentication Errors
    INVALID_API_KEY = "invalid_api_key"
    MISSING_API_KEY = "missing_api_key"
    API_KEY_EXPIRED = "api_key_expired"
    
    # Billing and Credit Errors
    INSUFFICIENT_CREDITS = "insufficient_credits"
    BILLING_LIMIT_REACHED = "billing_limit_reached"
    PAYMENT_REQUIRED = "payment_required"
    
    # Provider-specific Errors
    PROVIDER_UNAVAILABLE = "provider_unavailable"
    PROVIDER_TIMEOUT = "provider_timeout"
    PROVIDER_RATE_LIMITED = "provider_rate_limited"
    PROVIDER_MAINTENANCE = "provider_maintenance"
    
    # Content and Prompt Errors
    CONTENT_POLICY_VIOLATION = "content_policy_violation"
    INVALID_PROMPT = "invalid_prompt"
    PROMPT_TOO_LONG = "prompt_too_long"
    
    # Network and Technical Errors
    NETWORK_ERROR = "network_error"
    REQUEST_TIMEOUT = "request_timeout"
    RATE_LIMIT_EXCEEDED = "rate_limit_exceeded"
    
    # Processing Errors
    PROCESSING_ERROR = "processing_error"
    UNKNOWN_ERROR = "unknown_error"


@dataclass
class AIGenerationError:
    """Structured error information for AI generation failures."""
    
    error_type: AIGenerationErrorType
    message: str
    user_message: str
    provider: str
    suggested_action: str
    retry_possible: bool
    correlation_id: str
    timestamp: datetime
    metadata: Dict[str, Any] = None
    
    def __post_init__(self):
        if self.metadata is None:
            self.metadata = {}
    
    def to_dict(self) -> Dict[str, Any]:
        """Convert error to dictionary for API responses."""
        return {
            "error_type": self.error_type.value,
            "message": self.message,
            "user_message": self.user_message,
            "provider": self.provider,
            "suggested_action": self.suggested_action,
            "retry_possible": self.retry_possible,
            "correlation_id": self.correlation_id,
            "timestamp": self.timestamp.isoformat(),
            "metadata": self.metadata
        }
