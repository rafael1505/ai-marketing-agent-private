from typing import List, Optional, Dict, Any
from fastapi import APIRouter, HTTPException, Body
from pydantic import BaseModel
import logging

# Configure logging
logger = logging.getLogger(__name__)

# Create router
router = APIRouter()

# Mock function for user ID - in a real app, this would come from authentication
def get_current_user_id() -> str:
    """Mock function to return a user ID for development purposes"""
    return "1"

class AIProviderModel(BaseModel):
    name: str
    id: str
    logo: Optional[str] = None
    apiKey: Optional[str] = None
    isConfigured: Optional[bool] = False
    modelOptions: Optional[List[str]] = []
    selectedModel: Optional[str] = None
    maxTokens: Optional[int] = 1000
    temperature: Optional[float] = 0.7
    isActive: Optional[bool] = True

class ValidationRequest(BaseModel):
    providerId: str
    apiKey: str

# In-memory storage for development (would be replaced by real database)
PROVIDERS_STORAGE: Dict[str, List[Dict]] = {}

# Default providers for new users
DEFAULT_PROVIDERS = [
    {
        "name": "Stability AI",
        "id": "stability",
        "logo": "/ai-providers/stability.svg",
        "isConfigured": False,
        "selectedModel": "",
        "maxTokens": 1000,
        "temperature": 0.7,
        "isActive": True
    },
    {
        "name": "Hugging Face",
        "id": "huggingface",
        "logo": "/ai-providers/huggingface.svg",
        "isConfigured": False,
        "selectedModel": "",
        "maxTokens": 1000,
        "temperature": 0.7,
        "isActive": True
    }
]

def get_user_providers(user_id: str) -> List[Dict]:
    """Get providers for a user, creating defaults if none exist"""
    if user_id not in PROVIDERS_STORAGE:
        # Initialize with default providers
        PROVIDERS_STORAGE[user_id] = [p.copy() for p in DEFAULT_PROVIDERS]
    return PROVIDERS_STORAGE[user_id]

@router.get("", response_model=List[AIProviderModel])
async def get_user_ai_providers():
    """Get all AI providers configured for the current user"""
    try:
        user_id = get_current_user_id()
        logger.info(f"Getting AI providers for user {user_id}")
        
        providers = get_user_providers(user_id)
        
        # Don't return API keys in the list view
        safe_providers = []
        for provider in providers:
            safe_provider = provider.copy()
            if "apiKey" in safe_provider and safe_provider["apiKey"]:
                safe_provider["apiKey"] = "••••••••••••••••"
            safe_providers.append(safe_provider)
        
        logger.info(f"Returning {len(safe_providers)} providers")
        return safe_providers
    except Exception as e:
        logger.error(f"Error retrieving AI providers: {e}")
        return []

@router.get("/{provider_id}", response_model=AIProviderModel)
async def get_ai_provider(provider_id: str):
    """Get a specific AI provider by ID"""
    try:
        user_id = get_current_user_id()
        providers = get_user_providers(user_id)
        
        provider = next((p for p in providers if p["id"] == provider_id), None)
        if not provider:
            raise HTTPException(status_code=404, detail="Provider not found")
        
        # Mask the API key
        safe_provider = provider.copy()
        if "apiKey" in safe_provider and safe_provider["apiKey"]:
            safe_provider["apiKey"] = "••••••••••••••••"
        
        return safe_provider
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Error getting AI provider {provider_id}: {e}")
        raise HTTPException(status_code=500, detail=f"Error: {str(e)}")

@router.post("", response_model=AIProviderModel)
async def create_ai_provider(provider: AIProviderModel):
    """Create a new AI provider configuration"""
    try:
        user_id = get_current_user_id()
        providers = get_user_providers(user_id)
        
        # Check if provider already exists
        existing = next((p for p in providers if p["id"] == provider.id), None)
        if existing:
            raise HTTPException(status_code=400, detail="Provider with this ID already exists")
        
        # Add the new provider
        new_provider = provider.dict()
        providers.append(new_provider)
        
        # Return the created provider (without the API key for security)
        response = new_provider.copy()
        if "apiKey" in response and response["apiKey"]:
            response["apiKey"] = "••••••••••••••••"
        
        logger.info(f"Created new AI provider: {provider.id}")
        return response
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Error creating AI provider: {e}")
        raise HTTPException(status_code=500, detail=f"Error: {str(e)}")

@router.put("/{provider_id}", response_model=AIProviderModel)
async def update_ai_provider(provider_id: str, updates: Dict[str, Any] = Body(...)):
    """Update an existing AI provider configuration"""
    try:
        user_id = get_current_user_id()
        providers = get_user_providers(user_id)
        
        # Find the provider to update
        provider_index = next((i for i, p in enumerate(providers) if p["id"] == provider_id), None)
        if provider_index is None:
            raise HTTPException(status_code=404, detail="Provider not found")
        
        # Update the provider
        providers[provider_index].update(updates)
        updated_provider = providers[provider_index]
        
        # Return the updated provider (mask API key)
        response = updated_provider.copy()
        if "apiKey" in response and response["apiKey"]:
            response["apiKey"] = "••••••••••••••••"
        
        logger.info(f"Updated AI provider: {provider_id}")
        return response
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Error updating AI provider {provider_id}: {e}")
        raise HTTPException(status_code=500, detail=f"Error: {str(e)}")

@router.delete("/{provider_id}")
async def delete_ai_provider(provider_id: str):
    """Delete an AI provider configuration"""
    try:
        user_id = get_current_user_id()
        providers = get_user_providers(user_id)
        
        # Find and remove the provider
        provider_index = next((i for i, p in enumerate(providers) if p["id"] == provider_id), None)
        if provider_index is None:
            raise HTTPException(status_code=404, detail="Provider not found")
        
        providers.pop(provider_index)
        
        logger.info(f"Deleted AI provider: {provider_id}")
        return {"success": True}
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Error deleting AI provider {provider_id}: {e}")
        raise HTTPException(status_code=500, detail=f"Error: {str(e)}")

@router.post("/validate")
async def validate_api_key(validation: ValidationRequest):
    """Validate an API key for a provider"""
    try:
        logger.info(f"Validating API key for provider: {validation.providerId}")
        
        # Mock validation - in real app, would call provider's API
        if validation.apiKey == "invalid_key_test":
            return {"valid": False, "message": "Invalid API key"}
        
        if validation.apiKey == "connection_error_test":
            raise HTTPException(status_code=500, detail="Connection error")
        
        # Simple format validation for known providers
        if validation.providerId == "stability" and not validation.apiKey.startswith("sk-"):
            return {"valid": False, "message": "Invalid Stability API key format. Should start with 'sk-'"}
        
        if validation.providerId == "huggingface" and not validation.apiKey.startswith("hf_"):
            return {"valid": False, "message": "Invalid Hugging Face API key format. Should start with 'hf_'"}
        
        return {"valid": True, "message": "API key validated successfully"}
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Error validating API key: {e}")
        return {"valid": False, "message": f"Validation error: {str(e)}"}

@router.get("/{provider_id}/options")
async def get_provider_options(provider_id: str):
    """Get available options for a provider (models, sizes, etc)"""
    try:
        logger.info(f"Getting options for provider: {provider_id}")
        
        # Mock implementation returning different models based on provider ID
        provider_models = {
            "stability": [
                "stable-diffusion-xl-1024-v1-0",
                "stable-diffusion-xl-1024-v0-9",
                "stable-diffusion-v1-5"
            ],
            "huggingface": [
                "runwayml/stable-diffusion-v1-5",
                "CompVis/stable-diffusion-v1-4",
                "stabilityai/stable-diffusion-2-1"
            ],
            "replicate": [
                "stability-ai/sdxl",
                "stability-ai/stable-diffusion",
                "cjwbw/dreamshaper"
            ]
        }
        
        # Return models for the provider, or default models if not found
        models = provider_models.get(provider_id, ["default-model-1", "default-model-2"])
        
        return {"models": models}
    except Exception as e:
        logger.error(f"Error getting provider options for {provider_id}: {e}")
        return {"models": ["default-model"]}
