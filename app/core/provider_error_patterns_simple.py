"""Enhanced error pattern matching for different AI providers."""

import re
import uuid
from typing import Optional
from datetime import datetime

from .ai_generation_errors import AIGenerationError, AIGenerationErrorType

class ProviderErrorPatterns:
    @staticmethod
    def detect_openai_error(error_message: str) -> AIGenerationErrorType:
        if not error_message:
            return AIGenerationErrorType.UNKNOWN_ERROR
        
        error_message = str(error_message).lower()
        
        if "quota" in error_message and "exceeded" in error_message:
            return AIGenerationErrorType.BILLING_LIMIT_REACHED
        elif "insufficient" in error_message and "credits" in error_message:
            return AIGenerationErrorType.INSUFFICIENT_CREDITS
        elif "invalid" in error_message and "api" in error_message:
            return AIGenerationErrorType.INVALID_API_KEY
        else:
            return AIGenerationErrorType.UNKNOWN_ERROR

class EnhancedErrorClassifier:
    def __init__(self):
        self.provider_patterns = ProviderErrorPatterns()
    
    def classify_provider_error(self, error: Exception, provider: str) -> AIGenerationError:
        error_message = str(error)
        correlation_id = str(uuid.uuid4())[:8]
        
        if provider.lower() == "openai":
            error_type = self.provider_patterns.detect_openai_error(error_message)
        else:
            error_type = AIGenerationErrorType.UNKNOWN_ERROR
        
        user_message, suggested_actions = self._get_error_guidance(error_type, provider)
        
        metadata = {
            "provider": provider,
            "original_error": error_message,
            "timestamp": datetime.now().isoformat()
        }
        
        return AIGenerationError(
            error_type=error_type,
            correlation_id=correlation_id,
            user_message=user_message,
            technical_details=f"Provider: {provider}, Error: {error_message[:200]}",
            suggested_actions=suggested_actions,
            metadata=metadata
        )
    
    def _get_error_guidance(self, error_type: AIGenerationErrorType, provider: str):
        if error_type == AIGenerationErrorType.BILLING_LIMIT_REACHED:
            return (f"Your {provider.title()} account billing limit has been reached. You need to add credits to continue.",
                   [f"Visit your {provider.title()} dashboard to add credits", "Check your current usage and billing settings"])
        elif error_type == AIGenerationErrorType.INSUFFICIENT_CREDITS:
            return (f"Your {provider.title()} account has insufficient credits.",
                   [f"Add more credits to your {provider.title()} account", "Check your current credit balance"])
        elif error_type == AIGenerationErrorType.INVALID_API_KEY:
            return (f"The {provider.title()} API key is invalid or has expired.",
                   [f"Verify your {provider.title()} API key is correct", "Generate a new API key if necessary"])
        else:
            return (f"An unexpected error occurred with {provider.title()}.",
                   ["Try the request again", "Contact support if the issue persists"])