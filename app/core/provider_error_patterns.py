"""Enhanced error pattern matching for different AI providers."""""""""""""""



import reEnhanced error pattern matching for different AI providers.

import uuid

from typing import OptionalProvides provider-specific error detection, classification, and user-friendly messaging.Enhanced error detection patterns for AI providers.

from datetime import datetime

"""

from .ai_generation_errors import AIGenerationError, AIGenerationErrorType

Enhanced error detection patterns for AI providers.Enhanced error detection patterns for AI providers.

class ProviderErrorPatterns:

    @staticmethodimport re

    def detect_openai_error(error_message: str) -> AIGenerationErrorType:

        if not error_message:import uuidThis module provides provider-specific error pattern matching and classification

            return AIGenerationErrorType.UNKNOWN_ERROR

        from typing import Optional, Dict, Any

        error_message = str(error_message).lower()

        from datetime import datetimeto improve error message accuracy and user guidance.

        if "quota" in error_message and "exceeded" in error_message:

            return AIGenerationErrorType.BILLING_LIMIT_REACHED

        elif "insufficient" in error_message and "credits" in error_message:

            return AIGenerationErrorType.INSUFFICIENT_CREDITSfrom .ai_generation_errors import AIGenerationError, AIGenerationErrorType"""

        elif "invalid" in error_message and "api" in error_message:

            return AIGenerationErrorType.INVALID_API_KEY

        else:

            return AIGenerationErrorType.UNKNOWN_ERRORThis module provides provider-specific error pattern matching and classificationThis module provides provider-specific error pattern matching and classification



class EnhancedErrorClassifier:class ProviderErrorPatterns:

    def __init__(self):

        self.provider_patterns = ProviderErrorPatterns()    """Enhanced error pattern matching for different AI providers."""from typing import Dict, List, Optional, Tuple

    

    def classify_provider_error(self, error: Exception, provider: str) -> AIGenerationError:    

        error_message = str(error)

        correlation_id = str(uuid.uuid4())[:8]    @staticmethodimport reto improve error message accuracy and user guidance.to improve error message accuracy and user guidance.

        

        if provider.lower() == "openai":    def detect_openai_error(error_message: str) -> Optional[AIGenerationErrorType]:

            error_type = self.provider_patterns.detect_openai_error(error_message)

        else:        """Detect specific OpenAI error types from error message"""from app.core.ai_generation_errors import AIGenerationError, AIGenerationErrorType

            error_type = AIGenerationErrorType.UNKNOWN_ERROR

                if not error_message:

        user_message, suggested_action = self._get_error_guidance(error_type, provider)

                    return Nonefrom datetime import datetime""""""

        return AIGenerationError(

            error_type=error_type,        

            message=error_message,

            technical_details=f"Provider: {provider}, Error: {error_message[:200]}",        # Convert to string if it's an exception object

            user_message=user_message,

            provider=provider,        if hasattr(error_message, '__str__'):

            correlation_id=correlation_id,

            suggested_action=suggested_action,            error_message = str(error_message)

            retry_possible=error_type != AIGenerationErrorType.INVALID_API_KEY

        )            

    

    def _get_error_guidance(self, error_type: AIGenerationErrorType, provider: str):        error_message_lower = error_message.lower()class ProviderErrorPatterns:

        if error_type == AIGenerationErrorType.BILLING_LIMIT_REACHED:

            return (f"Your {provider.title()} account billing limit has been reached. You need to add credits to continue.",        

                   f"Visit your {provider.title()} dashboard to add credits")

        elif error_type == AIGenerationErrorType.INSUFFICIENT_CREDITS:        # Priority-based pattern matching for OpenAI errors    """Enhanced error pattern matching for different AI providers."""from typing import Dict, List, Optional, Tuplefrom typing import Dict, List, Optional, Tuple

            return (f"Your {provider.title()} account has insufficient credits.",

                   f"Add more credits to your {provider.title()} account")        error_patterns = [

        elif error_type == AIGenerationErrorType.INVALID_API_KEY:

            return (f"The {provider.title()} API key is invalid or has expired.",            # Billing and quota errors (highest priority)    

                   f"Verify your {provider.title()} API key is correct")

        else:            {

            return (f"An unexpected error occurred with {provider.title()}.",

                   "Try the request again")                "error_type": AIGenerationErrorType.BILLING_LIMIT_REACHED,    # OpenAI specific error patterns with priority (higher number = higher priority)import reimport re

                "patterns": [

                    r"quota.*exceeded",    OPENAI_PATTERNS = {

                    r"billing.*limit.*reached",

                    r"usage.*limit.*exceeded",        AIGenerationErrorType.BILLING_LIMIT_REACHED: {from app.core.ai_generation_errors import AIGenerationError, AIGenerationErrorTypefrom app.core.ai_generation_errors import AIGenerationError, AIGenerationErrorType

                    r"exceeded.*current.*quota",

                    r"account.*billing.*limit",            "patterns": [

                    r"credit.*limit.*reached",

                    r"monthly.*quota.*exceeded"                r"billing hard limit.*reached",from datetime import datetimefrom datetime import datetime

                ],

                "priority": 10                r"billing_hard_limit_reached",

            },

            # Insufficient credits (high priority)                r"exceeded.*billing.*limit",

            {

                "error_type": AIGenerationErrorType.INSUFFICIENT_CREDITS,                r"billing limit.*reached",

                "patterns": [

                    r"insufficient.*credits",                r"hard limit.*billing",

                    r"not.*enough.*credits",

                    r"credit.*balance.*insufficient",                r"account.*suspended.*billing"

                    r"account.*credits.*depleted",

                    r"add.*more.*credits",            ],class ProviderErrorPatterns:class ProviderErrorPatterns:

                    r"balance.*too.*low"

                ],            "priority": 10,

                "priority": 9

            },            "user_message": "Your OpenAI account billing limit has been reached. You need to add credits or increase your spending limit to continue using the service.",    """Enhanced error pattern matching for different AI providers."""    """Enhanced error pattern matching for different AI providers."""

            # API Key errors (high priority)

            {            "suggested_action": "Visit your OpenAI dashboard at https://platform.openai.com/account/billing to add credits or increase your spending limit",

                "error_type": AIGenerationErrorType.INVALID_API_KEY,

                "patterns": [            "retry_possible": False        

                    r"invalid.*api.*key",

                    r"unauthorized.*access",        },

                    r"authentication.*failed",

                    r"api.*key.*invalid",        AIGenerationErrorType.INSUFFICIENT_CREDITS: {    # OpenAI specific error patterns with priority (higher number = higher priority)    # OpenAI specific error patterns with priority (higher number = higher priority)

                    r"incorrect.*api.*key",

                    r"expired.*api.*key"            "patterns": [

                ],

                "priority": 8                r"insufficient.*credits",    OPENAI_PATTERNS = {    OPENAI_PATTERNS = {

            },

            # Rate limiting (medium priority)                r"not enough.*credits",

            {

                "error_type": AIGenerationErrorType.RATE_LIMIT_EXCEEDED,                r"credit.*insufficient",        AIGenerationErrorType.BILLING_LIMIT_REACHED: {        AIGenerationErrorType.BILLING_LIMIT_REACHED: {

                "patterns": [

                    r"rate.*limit.*exceeded",                r"out of.*credits",

                    r"too.*many.*requests",

                    r"request.*limit.*exceeded",                r"credit.*balance.*low",            "patterns": [            "patterns": [

                    r"throttled.*request"

                ],                r"insufficient_quota"

                "priority": 7

            },            ],                r"billing hard limit.*reached",                r"billing hard limit.*reached",

            # Server errors (lower priority)

            {            "priority": 9,

                "error_type": AIGenerationErrorType.SERVICE_UNAVAILABLE,

                "patterns": [            "user_message": "Your OpenAI account does not have sufficient credits to complete this request.",                r"billing_hard_limit_reached",                r"billing_hard_limit_reached",

                    r"service.*unavailable",

                    r"server.*error",            "suggested_action": "Add credits to your OpenAI account at https://platform.openai.com/account/billing",

                    r"internal.*error",

                    r"503.*service.*unavailable"            "retry_possible": False                r"exceeded.*billing.*limit",                r"exceeded.*billing.*limit",

                ],

                "priority": 5        },

            }

        ]        AIGenerationErrorType.INVALID_API_KEY: {                r"billing limit.*reached",                r"billing limit.*reached",

        

        # Sort by priority and find first match            "patterns": [

        error_patterns.sort(key=lambda x: x["priority"], reverse=True)

                        r"invalid.*api.*key",                r"hard limit.*billing",                r"hard limit.*billing",

        for pattern_config in error_patterns:

            for pattern in pattern_config["patterns"]:                r"incorrect api key",

                if re.search(pattern, error_message_lower):

                    return pattern_config["error_type"]                r"api.*key.*invalid",                r"account.*suspended.*billing"                r"account.*suspended.*billing"

        

        return AIGenerationErrorType.UNKNOWN_ERROR                r"authentication.*failed",



                r"invalid.*authentication",            ],            ],

class EnhancedErrorClassifier:

    """Enhanced error classification system with provider-specific patterns."""                r"unauthorized.*api.*key"

    

    def __init__(self):            ],            "priority": 10,            "priority": 10,

        self.provider_patterns = ProviderErrorPatterns()

                "priority": 8,

    def classify_provider_error(self, error: Exception, provider: str) -> AIGenerationError:

        """            "user_message": "The OpenAI API key is invalid or has expired.",            "user_message": "Your OpenAI account billing limit has been reached. You need to add credits or increase your spending limit to continue using the service.",            "user_message": "Your OpenAI account billing limit has been reached. You need to add credits or increase your spending limit to continue using the service.",

        Classify an error from a specific AI provider.

                    "suggested_action": "Check your API key configuration in the AI Settings page",

        Args:

            error: The exception or error object            "retry_possible": False            "suggested_action": "Visit your OpenAI dashboard at https://platform.openai.com/account/billing to add credits or increase your spending limit",            "suggested_action": "Visit your OpenAI dashboard at https://platform.openai.com/account/billing to add credits or increase your spending limit",

            provider: The AI provider name (e.g., 'openai', 'stability')

                    },

        Returns:

            AIGenerationError: Structured error with user-friendly message        AIGenerationErrorType.RATE_LIMIT_EXCEEDED: {            "retry_possible": False            "retry_possible": False,

        """

        error_message = str(error)            "patterns": [

        correlation_id = str(uuid.uuid4())[:8]

                        r"rate.*limit.*exceeded",        },            "help_url": "https://platform.openai.com/account/billing"

        # Provider-specific error detection

        if provider.lower() == 'openai':                r"too many.*requests",

            error_type = self.provider_patterns.detect_openai_error(error_message)

        else:                r"quota.*exceeded",        AIGenerationErrorType.INSUFFICIENT_CREDITS: {        },

            error_type = AIGenerationErrorType.UNKNOWN_ERROR

                        r"rate_limit_exceeded",

        # Generate user-friendly messages and actions

        user_message, suggested_actions = self._get_error_guidance(error_type, provider)                r"requests.*per.*minute.*exceeded"            "patterns": [        AIGenerationErrorType.INSUFFICIENT_CREDITS: {

        

        # Create metadata            ],

        metadata = {

            "provider": provider,            "priority": 7,                r"insufficient.*credits",            "patterns": [

            "original_error": error_message,

            "timestamp": datetime.now().isoformat(),            "user_message": "OpenAI rate limit exceeded. Please wait a moment before trying again.",

            "error_classification_version": "2.0"

        }            "suggested_action": "Wait a few minutes and retry, or upgrade your OpenAI plan for higher limits",                r"not enough.*credits",                r"insufficient.*credits",

        

        return AIGenerationError(            "retry_possible": True

            error_type=error_type,

            correlation_id=correlation_id,        },                r"credit.*insufficient",                r"quota.*exceeded",

            user_message=user_message,

            technical_details=f"Provider: {provider}, Error: {error_message[:200]}...",        AIGenerationErrorType.CONTENT_POLICY_VIOLATION: {

            suggested_actions=suggested_actions,

            metadata=metadata            "patterns": [                r"out of.*credits",                r"usage.*limit.*exceeded",

        )

                    r"content.*policy.*violation",

    def _get_error_guidance(self, error_type: AIGenerationErrorType, provider: str) -> tuple[str, list[str]]:

        """Get user-friendly error messages and suggested actions."""                r"safety.*system",                r"credit.*balance.*low",                r"not.*enough.*credits",

        

        error_guidance = {                r"content.*filtered",

            AIGenerationErrorType.BILLING_LIMIT_REACHED: {

                "message": f"Your {provider.title()} account billing limit has been reached. You need to add credits or increase your spending limit to continue using the service.",                r"policy.*violation",                r"insufficient_quota"                r"credits.*exhausted",

                "actions": [

                    f"Visit your {provider.title()} dashboard to add credits or increase your spending limit",                r"inappropriate.*content"

                    "Check your current usage and billing settings",

                    "Consider upgrading to a higher tier plan if available"            ],            ],                r"insufficient.*balance"

                ]

            },            "priority": 6,

            AIGenerationErrorType.INSUFFICIENT_CREDITS: {

                "message": f"Your {provider.title()} account has insufficient credits to complete this request.",            "user_message": "The content request violates OpenAI's usage policies.",            "priority": 9,            ],

                "actions": [

                    f"Add more credits to your {provider.title()} account",            "suggested_action": "Modify your prompt to comply with OpenAI's content policy",

                    "Check your current credit balance",

                    "Consider setting up automatic billing to avoid interruptions"            "retry_possible": True            "user_message": "Your OpenAI account does not have sufficient credits to complete this request.",            "priority": 9,

                ]

            },        },

            AIGenerationErrorType.INVALID_API_KEY: {

                "message": f"The {provider.title()} API key is invalid or has expired.",        AIGenerationErrorType.PROCESSING_ERROR: {            "suggested_action": "Add credits to your OpenAI account at https://platform.openai.com/account/billing",            "user_message": "Your OpenAI account has insufficient credits to generate images. Please add credits to your account.",

                "actions": [

                    f"Verify your {provider.title()} API key is correct",            "patterns": [

                    "Check if your API key has expired",

                    "Generate a new API key if necessary"                r"internal.*error",            "retry_possible": False            "suggested_action": "Add credits to your OpenAI account at https://platform.openai.com/account/billing",

                ]

            },                r"server.*error",

            AIGenerationErrorType.RATE_LIMIT_EXCEEDED: {

                "message": f"You've exceeded the rate limit for {provider.title()}. Please wait a moment before trying again.",                r"processing.*failed",        },            "retry_possible": False,

                "actions": [

                    "Wait a few minutes before making another request",                r"unexpected.*error",

                    "Consider reducing the frequency of your requests",

                    "Upgrade to a higher tier plan for increased rate limits"                r"service.*unavailable"        AIGenerationErrorType.INVALID_API_KEY: {            "help_url": "https://platform.openai.com/account/billing"

                ]

            },            ],

            AIGenerationErrorType.SERVICE_UNAVAILABLE: {

                "message": f"The {provider.title()} service is currently unavailable. This is usually temporary.",            "priority": 3,            "patterns": [        },

                "actions": [

                    "Try again in a few minutes",            "user_message": "An error occurred while processing your request.",

                    f"Check {provider.title()}'s status page for service updates",

                    "Contact support if the issue persists"            "suggested_action": "Try again in a few moments, or contact support if the issue persists",                r"invalid.*api.*key",        AIGenerationErrorType.INVALID_API_KEY: {

                ]

            }            "retry_possible": True

        }

                }                r"incorrect api key",            "patterns": [

        guidance = error_guidance.get(error_type, {

            "message": f"An unexpected error occurred with {provider.title()}. Please try again.",    }

            "actions": [

                "Try the request again",                r"api.*key.*invalid",                r"incorrect.*api.*key",

                "Check your internet connection",

                "Contact support if the issue persists"    @classmethod

            ]

        })    def detect_openai_error(cls, error_message: str) -> Optional[Tuple[AIGenerationErrorType, Dict]]:                r"authentication.*failed",                r"invalid.*api.*key", 

        

        return guidance["message"], guidance["actions"]        """

        Detect OpenAI-specific error patterns with priority-based matching.                r"invalid.*authentication",                r"unauthorized",

        

        Args:                r"unauthorized.*api.*key"                r"authentication.*failed",

            error_message: The error message to analyze

                        ],                r"invalid.*authentication",

        Returns:

            Tuple of (error_type, pattern_info) if match found, None otherwise            "priority": 8,                r"api.*key.*invalid"

        """

        error_message_lower = error_message.lower()            "user_message": "The OpenAI API key is invalid or has expired.",            ],

        

        # Sort patterns by priority (highest first)            "suggested_action": "Check your API key configuration in the AI Settings page",            "priority": 8,

        sorted_patterns = sorted(

            cls.OPENAI_PATTERNS.items(),             "retry_possible": False            "user_message": "Your OpenAI API key is invalid or incorrect. Please check your API key configuration.",

            key=lambda x: x[1]["priority"], 

            reverse=True        },            "suggested_action": "Go to AI Configuration and update your OpenAI API key. You can find your API key at https://platform.openai.com/api-keys",

        )

                AIGenerationErrorType.RATE_LIMIT_EXCEEDED: {            "retry_possible": False,

        for error_type, pattern_info in sorted_patterns:

            for pattern in pattern_info["patterns"]:            "patterns": [            "help_url": "https://platform.openai.com/api-keys"

                if re.search(pattern, error_message_lower):

                    return error_type, pattern_info                r"rate.*limit.*exceeded",        },

                    

        return None                r"too many.*requests",        AIGenerationErrorType.API_KEY_EXPIRED: {



    @classmethod                r"quota.*exceeded",            "patterns": [

    def detect_generic_error(cls, error_message: str) -> Tuple[AIGenerationErrorType, Dict]:

        """                r"rate_limit_exceeded",                r"api.*key.*expired",

        Fallback for generic error detection when provider-specific patterns don't match.

                        r"requests.*per.*minute.*exceeded"                r"token.*expired",

        Args:

            error_message: The error message to analyze            ],                r"authentication.*expired",

            

        Returns:            "priority": 7,                r"expired.*credentials"

            Tuple of (error_type, generic_info)

        """            "user_message": "OpenAI rate limit exceeded. Please wait a moment before trying again.",            ],

        error_message_lower = error_message.lower()

                    "suggested_action": "Wait a few minutes and retry, or upgrade your OpenAI plan for higher limits",            "priority": 8,

        # Generic patterns

        if any(word in error_message_lower for word in ["network", "connection", "timeout"]):            "retry_possible": True            "user_message": "Your OpenAI API key has expired. Please generate a new API key.",

            return AIGenerationErrorType.NETWORK_ERROR, {

                "user_message": "Network connection error occurred.",        },            "suggested_action": "Generate a new API key at https://platform.openai.com/api-keys and update your configuration",

                "suggested_action": "Check your internet connection and try again",

                "retry_possible": True        AIGenerationErrorType.CONTENT_POLICY_VIOLATION: {            "retry_possible": False,

            }

        elif any(word in error_message_lower for word in ["permission", "access", "denied"]):            "patterns": [            "help_url": "https://platform.openai.com/api-keys"

            return AIGenerationErrorType.MISSING_API_KEY, {

                "user_message": "Access denied or permission error.",                r"content.*policy.*violation",        },

                "suggested_action": "Check your API key configuration",

                "retry_possible": False                r"safety.*system",        AIGenerationErrorType.PROVIDER_RATE_LIMITED: {

            }

        else:                r"content.*filtered",            "patterns": [

            return AIGenerationErrorType.PROCESSING_ERROR, {

                "user_message": "An unexpected error occurred during image generation.",                r"policy.*violation",                r"rate.*limit.*exceeded",

                "suggested_action": "Try again or contact support if the issue persists",

                "retry_possible": True                r"inappropriate.*content"                r"too.*many.*requests",

            }

            ],                r"429.*too.*many.*requests",



class EnhancedErrorClassifier:            "priority": 6,                r"request.*limit.*exceeded",

    """Main class for enhanced error classification across providers."""

                "user_message": "The content request violates OpenAI's usage policies.",                r"rate.*exceeded"

    @staticmethod

    def classify_provider_error(            "suggested_action": "Modify your prompt to comply with OpenAI's content policy",            ],

        error_message: str, 

        provider: str,             "retry_possible": True            "priority": 7,

        correlation_id: Optional[str] = None

    ) -> AIGenerationError:        },            "user_message": "You've made too many requests to OpenAI. Please wait a few minutes before trying again.",

        """

        Classify provider-specific errors with enhanced pattern matching.        AIGenerationErrorType.PROCESSING_ERROR: {            "suggested_action": "Wait 2-3 minutes before retrying, or consider upgrading your OpenAI plan for higher rate limits",

        

        Args:            "patterns": [            "retry_possible": True,

            error_message: The error message to classify

            provider: The AI provider that generated the error                r"internal.*error",            "help_url": "https://platform.openai.com/docs/guides/rate-limits"

            correlation_id: Optional correlation ID for tracking

                            r"server.*error",        },

        Returns:

            AIGenerationError with enhanced classification                r"processing.*failed",        AIGenerationErrorType.CONTENT_POLICY_VIOLATION: {

        """

        detected_error = None                r"unexpected.*error",            "patterns": [

        

        # Provider-specific detection                r"service.*unavailable"                r"content.*policy.*violation",

        if provider.lower() == "openai":

            detected_error = ProviderErrorPatterns.detect_openai_error(error_message)            ],                r"policy.*violation",

        

        # Fallback to generic detection            "priority": 3,                r"inappropriate.*content",

        if detected_error is None:

            error_type, pattern_info = ProviderErrorPatterns.detect_generic_error(error_message)            "user_message": "An error occurred while processing your request.",                r"content.*filter",

            detected_error = (error_type, pattern_info)

        else:            "suggested_action": "Try again in a few moments, or contact support if the issue persists",                r"safety.*filter",

            error_type, pattern_info = detected_error

                    "retry_possible": True                r"violated.*usage.*policies"

        # Create enhanced error with additional metadata

        return AIGenerationError(        }            ],

            error_type=error_type,

            message=error_message,    }            "priority": 6,

            user_message=pattern_info["user_message"],

            provider=provider,            "user_message": "Your prompt violates OpenAI's content policy. Please modify your prompt to remove potentially inappropriate content.",

            suggested_action=pattern_info["suggested_action"],

            retry_possible=pattern_info.get("retry_possible", True),    @classmethod            "suggested_action": "Review OpenAI's usage policies and modify your prompt to be more appropriate",

            correlation_id=correlation_id or f"err_{datetime.now().strftime('%Y%m%d_%H%M%S')}",

            timestamp=datetime.now(),    def detect_openai_error(cls, error_message: str) -> Optional[Tuple[AIGenerationErrorType, Dict]]:            "retry_possible": True,

            metadata={

                "pattern_matched": True,        """            "help_url": "https://openai.com/policies/usage-policies"

                "provider_specific": provider.lower() in ["openai"],

                "error_category": error_type.value        Detect OpenAI-specific error patterns with priority-based matching.        },

            }

        )                AIGenerationErrorType.PROVIDER_UNAVAILABLE: {



    @staticmethod         Args:            "patterns": [

    def create_fallback_error(

        error_message: str,             error_message: The error message to analyze                r"service.*unavailable",

        provider: str, 

        correlation_id: Optional[str] = None                            r"server.*error",

    ) -> AIGenerationError:

        """        Returns:                r"internal.*server.*error",

        Create a fallback error when pattern matching fails.

                    Tuple of (error_type, pattern_info) if match found, None otherwise                r"500.*internal.*server",

        Args:

            error_message: The original error message        """                r"502.*bad.*gateway",

            provider: The AI provider

            correlation_id: Optional correlation ID        error_message_lower = error_message.lower()                r"503.*service.*unavailable",

            

        Returns:                        r"server.*had.*an.*error"

            AIGenerationError with fallback classification

        """        # Sort patterns by priority (highest first)            ],

        return AIGenerationError(

            error_type=AIGenerationErrorType.PROCESSING_ERROR,        sorted_patterns = sorted(            "priority": 5,

            message=error_message,

            user_message="An error occurred during image generation. Please try again.",            cls.OPENAI_PATTERNS.items(),             "user_message": "OpenAI's service is temporarily unavailable. This is usually a temporary issue.",

            provider=provider,

            suggested_action="Try again or contact support if the issue persists",            key=lambda x: x[1]["priority"],             "suggested_action": "Wait a few minutes and try again, or check OpenAI's status page for service updates",

            retry_possible=True,

            correlation_id=correlation_id or f"fallback_{datetime.now().strftime('%Y%m%d_%H%M%S')}",            reverse=True            "retry_possible": True,

            timestamp=datetime.now(),

            metadata={        )            "help_url": "https://status.openai.com/"

                "pattern_matched": False,

                "fallback_error": True,                },

                "original_message": error_message[:200]  # Truncate for safety

            }        for error_type, pattern_info in sorted_patterns:        AIGenerationErrorType.PROVIDER_TIMEOUT: {

        )
            for pattern in pattern_info["patterns"]:            "patterns": [

                if re.search(pattern, error_message_lower):                r"timeout",

                    return error_type, pattern_info                r"request.*timeout",

                                    r"connection.*timeout",

        return None                r"gateway.*timeout",

                r"504.*gateway.*timeout"

    @classmethod            ],

    def detect_generic_error(cls, error_message: str) -> Tuple[AIGenerationErrorType, Dict]:            "priority": 4,

        """            "user_message": "The request to OpenAI timed out. This might be due to high server load.",

        Fallback for generic error detection when provider-specific patterns don't match.            "suggested_action": "Try again in a few moments. If the problem persists, OpenAI may be experiencing high load",

                    "retry_possible": True,

        Args:            "help_url": "https://status.openai.com/"

            error_message: The error message to analyze        }

                }

        Returns:    

            Tuple of (error_type, generic_info)    @classmethod

        """    def detect_openai_error(cls, error_message: str, status_code: Optional[int] = None) -> Optional[AIGenerationError]:

        error_message_lower = error_message.lower()        """

                Detect and classify OpenAI-specific errors with enhanced accuracy.

        # Generic patterns        

        if any(word in error_message_lower for word in ["network", "connection", "timeout"]):        Args:

            return AIGenerationErrorType.NETWORK_ERROR, {            error_message: The error message from OpenAI API

                "user_message": "Network connection error occurred.",            status_code: HTTP status code if available

                "suggested_action": "Check your internet connection and try again",            

                "retry_possible": True        Returns:

            }            AIGenerationError or None if no specific pattern matches

        elif any(word in error_message_lower for word in ["permission", "access", "denied"]):        """

            return AIGenerationErrorType.MISSING_API_KEY, {        if not error_message:

                "user_message": "Access denied or permission error.",            return None

                "suggested_action": "Check your API key configuration",            

                "retry_possible": False        error_message_lower = error_message.lower()

            }        best_match = None

        else:        highest_priority = 0

            return AIGenerationErrorType.PROCESSING_ERROR, {        

                "user_message": "An unexpected error occurred during image generation.",        # Try to match error patterns with priority

                "suggested_action": "Try again or contact support if the issue persists",        for error_type, config in cls.OPENAI_PATTERNS.items():

                "retry_possible": True            for pattern in config["patterns"]:

            }                if re.search(pattern, error_message_lower):

                    if config["priority"] > highest_priority:

                        highest_priority = config["priority"]

class EnhancedErrorClassifier:                        best_match = (error_type, config)

    """Main class for enhanced error classification across providers."""                        break

            

    @staticmethod        if best_match:

    def classify_provider_error(            error_type, config = best_match

        error_message: str,             

        provider: str,             return AIGenerationError(

        correlation_id: Optional[str] = None                error_type=error_type,

    ) -> AIGenerationError:                message=error_message,

        """                technical_details=f"OpenAI API Error: {error_message} (Status: {status_code})",

        Classify provider-specific errors with enhanced pattern matching.                user_message=config["user_message"],

                        provider="openai",

        Args:                suggested_action=config["suggested_action"],

            error_message: The error message to classify                retry_possible=config["retry_possible"],

            provider: The AI provider that generated the error                timestamp=datetime.utcnow()

            correlation_id: Optional correlation ID for tracking            )

                    

        Returns:        return None

            AIGenerationError with enhanced classification    

        """    @classmethod

        detected_error = None    def get_provider_guidance(cls, provider: str) -> Dict[str, str]:

                """Get provider-specific setup and billing guidance."""

        # Provider-specific detection        guidance = {

        if provider.lower() == "openai":            "openai": {

            detected_error = ProviderErrorPatterns.detect_openai_error(error_message)                "name": "OpenAI",

                        "api_key_url": "https://platform.openai.com/api-keys",

        # Fallback to generic detection                "billing_url": "https://platform.openai.com/account/billing",

        if detected_error is None:                "status_url": "https://status.openai.com/",

            error_type, pattern_info = ProviderErrorPatterns.detect_generic_error(error_message)                "docs_url": "https://platform.openai.com/docs",

            detected_error = (error_type, pattern_info)                "pricing_url": "https://openai.com/pricing",

        else:                "setup_instructions": "1. Go to OpenAI Platform\n2. Create an API key\n3. Add billing information\n4. Set spending limits"

            error_type, pattern_info = detected_error            },

                    "stability": {

        # Create enhanced error with additional metadata                "name": "Stability AI",

        return AIGenerationError(                "api_key_url": "https://platform.stability.ai/account/keys",

            error_type=error_type,                "billing_url": "https://platform.stability.ai/account/credits",

            message=error_message,                "status_url": "https://status.stability.ai/",

            user_message=pattern_info["user_message"],                "docs_url": "https://platform.stability.ai/docs",

            provider=provider,                "pricing_url": "https://platform.stability.ai/pricing",

            suggested_action=pattern_info["suggested_action"],                "setup_instructions": "1. Go to Stability AI Platform\n2. Create an API key\n3. Purchase credits\n4. Configure usage limits"

            retry_possible=pattern_info.get("retry_possible", True),            },

            correlation_id=correlation_id or f"err_{datetime.now().strftime('%Y%m%d_%H%M%S')}",            "replicate": {

            timestamp=datetime.now(),                "name": "Replicate",

            metadata={                "api_key_url": "https://replicate.com/account/api-tokens",

                "pattern_matched": True,                "billing_url": "https://replicate.com/account/billing",

                "provider_specific": provider.lower() in ["openai"],                "status_url": "https://status.replicate.com/",

                "error_category": error_type.value                "docs_url": "https://replicate.com/docs",

            }                "pricing_url": "https://replicate.com/pricing",

        )                "setup_instructions": "1. Go to Replicate\n2. Create an API token\n3. Add payment method\n4. Monitor usage"

            }

    @staticmethod         }

    def create_fallback_error(        

        error_message: str,         return guidance.get(provider, {

        provider: str,             "name": provider.title(),

        correlation_id: Optional[str] = None            "setup_instructions": "Please check the provider's documentation for setup instructions"

    ) -> AIGenerationError:        })

        """

        Create a fallback error when pattern matching fails.

        class EnhancedErrorClassifier:

        Args:    """Enhanced error classifier with provider-specific logic."""

            error_message: The original error message    

            provider: The AI provider    @staticmethod

            correlation_id: Optional correlation ID    def classify_provider_error(

                    error_message: str,

        Returns:        provider: str,

            AIGenerationError with fallback classification        status_code: Optional[int] = None,

        """        response_data: Optional[Dict] = None

        return AIGenerationError(    ) -> AIGenerationError:

            error_type=AIGenerationErrorType.PROCESSING_ERROR,        """

            message=error_message,        Classify errors with provider-specific logic.

            user_message="An error occurred during image generation. Please try again.",        

            provider=provider,        Args:

            suggested_action="Try again or contact support if the issue persists",            error_message: Error message from the provider

            retry_possible=True,            provider: Provider name (openai, stability, etc.)

            correlation_id=correlation_id or f"fallback_{datetime.now().strftime('%Y%m%d_%H%M%S')}",            status_code: HTTP status code

            timestamp=datetime.now(),            response_data: Full response data if available

            metadata={            

                "pattern_matched": False,        Returns:

                "fallback_error": True,            AIGenerationError with detailed classification

                "original_message": error_message[:200]  # Truncate for safety        """

            }        # Try provider-specific detection first

        )        if provider.lower() == "openai":
            specific_error = ProviderErrorPatterns.detect_openai_error(error_message, status_code)
            if specific_error:
                return specific_error
        
        # Fallback to generic classification
        return AIGenerationError(
            error_type=AIGenerationErrorType.UNKNOWN_ERROR,
            message=error_message,
            technical_details=f"{provider} API Error: {error_message} (Status: {status_code})",
            user_message=f"An error occurred with {provider}: {error_message}",
            provider=provider,
            suggested_action="Try again or contact support if the problem persists",
            retry_possible=True,
            timestamp=datetime.utcnow()
        )