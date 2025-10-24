from typing import List, Optional
from fastapi import APIRouter, Depends, HTTPException, Body, Request
from pydantic import BaseModel
from app.api.v1.deps import get_current_user
import logging

router = APIRouter()
logger = logging.getLogger(__name__)

class AIProviderModel(BaseModel):
    name: str
    id: str
    logo: Optional[str] = None
    apiKey: Optional[str] = None
    baseUrl: Optional[str] = None
    isConfigured: Optional[bool] = False
    modelOptions: Optional[List[str]] = []
    selectedModel: Optional[str] = None
    maxTokens: Optional[int] = 1000
    temperature: Optional[float] = 0.7
    isActive: Optional[bool] = True
    quality: Optional[str] = None
    size: Optional[str] = None
    style: Optional[str] = None
    customOptions: Optional[dict] = None

class ValidationRequest(BaseModel):
    providerId: str
    apiKey: str

@router.get("/api/v1/ai-providers", response_model=List[AIProviderModel])
async def get_user_ai_providers(request: Request, current_user: dict = Depends(get_current_user)):
    """Get all AI providers configured for the current user"""
    try:
        db = request.app.mongodb
        collection = db.ai_providers
        
        # Extract user_id from user object
        current_user_id = str(current_user.get("_id") or current_user.get("id") or "1")
        
        # Query providers for this user
        cursor = collection.find({"user_id": current_user_id})
        providers = await cursor.to_list(length=None)
        
        logger.info(f"Found {len(providers)} AI providers for user {current_user_id}")
        
        # Don't return actual API keys in the list view - mask them
        result = []
        for provider in providers:
            provider_copy = dict(provider)
            # Remove MongoDB _id field
            provider_copy.pop("_id", None)
            provider_copy.pop("user_id", None)
            
            # Mask API key if present
            if "apiKey" in provider_copy and provider_copy["apiKey"]:
                provider_copy["apiKey"] = "••••••••••••••••"
            
            result.append(provider_copy)
        
        return result
    except Exception as e:
        logger.error(f"Error fetching AI providers: {e}")
        return []

@router.get("/api/v1/ai-providers/{provider_id}", response_model=AIProviderModel)
async def get_ai_provider(provider_id: str, request: Request, current_user: dict = Depends(get_current_user)):
    """Get a specific AI provider by ID"""
    try:
        db = request.app.mongodb
        collection = db.ai_providers
        
        current_user_id = str(current_user.get("_id") or current_user.get("id") or "1")
        provider = await collection.find_one({"user_id": current_user_id, "id": provider_id})
        
        if not provider:
            raise HTTPException(status_code=404, detail="Provider not found")
        
        # Remove MongoDB _id and user_id fields
        provider.pop("_id", None)
        provider.pop("user_id", None)
        
        # Mask the API key
        if "apiKey" in provider and provider["apiKey"]:
            provider["apiKey"] = "••••••••••••••••"
        
        return provider
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Error fetching AI provider {provider_id}: {e}")
        raise HTTPException(status_code=500, detail="Internal server error")

@router.post("/api/v1/ai-providers", response_model=AIProviderModel)
async def create_ai_provider(provider: AIProviderModel, request: Request, current_user: dict = Depends(get_current_user)):
    """Create a new AI provider configuration"""
    try:
        db = request.app.mongodb
        collection = db.ai_providers
        
        current_user_id = str(current_user.get("_id") or current_user.get("id") or "1")
        # Check if provider with this ID already exists for this user
        existing = await collection.find_one({"user_id": current_user_id, "id": provider.id})
        if existing:
            raise HTTPException(status_code=400, detail="Provider with this ID already exists")
        
        # Convert model to dict and add user_id
        provider_dict = provider.dict()
        provider_dict["user_id"] = current_user_id
        
        # Insert into database
        await collection.insert_one(provider_dict)
        
        # Persist to disk
        
        logger.info(f"Created AI provider {provider.id} for user {current_user_id}")
        
        # Return the created provider (without the API key)
        provider_copy = provider_dict.copy()
        provider_copy.pop("_id", None)
        provider_copy.pop("user_id", None)
        if "apiKey" in provider_copy and provider_copy["apiKey"]:
            provider_copy["apiKey"] = "••••••••••••••••"
        
        return provider_copy
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Error creating AI provider: {e}")
        raise HTTPException(status_code=500, detail="Internal server error")

@router.put("/api/v1/ai-providers/{provider_id}", response_model=AIProviderModel)
async def update_ai_provider(
    provider_id: str, 
    request: Request,
    updates: dict = Body(...), 
    current_user: dict = Depends(get_current_user)
):
    """Update an existing AI provider configuration"""
    try:
        db = request.app.mongodb
        collection = db.ai_providers
        
        current_user_id = str(current_user.get("_id") or current_user.get("id") or "1")
        logger.info(f"Updating AI provider {provider_id} for user {current_user_id} with updates: {updates}")
        
        # Find the provider first
        existing_provider = await collection.find_one({"user_id": current_user_id, "id": provider_id})
        
        if not existing_provider:
            # If provider doesn't exist, create it
            logger.info(f"Provider {provider_id} not found, creating new one")
            provider_dict = {
                "id": provider_id,
                "user_id": current_user_id,
                **updates
            }
            await collection.insert_one(provider_dict)
        else:
            # Update existing provider
            await collection.update_one(
                {"user_id": current_user_id, "id": provider_id},
                {"$set": updates}
            )
        
        # Persist to disk
        
        logger.info(f"Successfully updated AI provider {provider_id}")
        
        # Fetch the updated provider
        updated_provider = await collection.find_one({"user_id": current_user_id, "id": provider_id})
        
        # Remove MongoDB _id and user_id fields
        updated_provider.pop("_id", None)
        updated_provider.pop("user_id", None)
        
        # Return the updated provider (with masked API key)
        if "apiKey" in updated_provider and updated_provider["apiKey"]:
            updated_provider["apiKey"] = "••••••••••••••••"
        
        return updated_provider
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Error updating AI provider {provider_id}: {e}")
        raise HTTPException(status_code=500, detail="Internal server error")

@router.delete("/api/v1/ai-providers/{provider_id}")
async def delete_ai_provider(provider_id: str, request: Request, current_user: dict = Depends(get_current_user)):
    """Delete an AI provider configuration"""
    try:
        db = request.app.mongodb
        collection = db.ai_providers
        
        current_user_id = str(current_user.get("_id") or current_user.get("id") or "1")
        # Delete the provider
        result = await collection.delete_one({"user_id": current_user_id, "id": provider_id})
        
        if result.deleted_count == 0:
            raise HTTPException(status_code=404, detail="Provider not found")
        
        # Persist to disk
        
        logger.info(f"Deleted AI provider {provider_id} for user {current_user_id}")
        
        return {"success": True}
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Error deleting AI provider {provider_id}: {e}")
        raise HTTPException(status_code=500, detail="Internal server error")

@router.post("/api/v1/ai-providers/validate")
def validate_api_key(validation: ValidationRequest, current_user: dict = Depends(get_current_user)):
    """Validate an API key for a provider"""
    current_user_id = str(current_user.get("_id") or current_user.get("id") or "1")
    # This is just a mock implementation
    # In a real app, you would call the provider's API to validate the key
    
    # Simulate validation success for most keys, but fail for specific test cases
    if validation.apiKey == "invalid_key_test":
        return {"valid": False, "message": "Invalid API key"}
    
    if validation.apiKey == "connection_error_test":
        raise HTTPException(status_code=500, detail="Connection error")
    
    # For stability.ai, check if key starts with "sk-" as a simple validation
    if validation.providerId == "stability" and not validation.apiKey.startswith("sk-"):
        return {"valid": False, "message": "Invalid Stability API key format. Should start with 'sk-'"}
    
    # For HuggingFace, check if key starts with "hf_" as a simple validation
    if validation.providerId == "huggingface" and not validation.apiKey.startswith("hf_"):
        return {"valid": False, "message": "Invalid Hugging Face API key format. Should start with 'hf_'"}
        
    return {"valid": True, "message": "API key validated successfully"}

@router.get("/api/v1/ai-providers/{provider_id}/options")
def get_provider_options(provider_id: str, current_user: dict = Depends(get_current_user)):
    """Get available options for a provider (models, sizes, etc)"""
    current_user_id = str(current_user.get("_id") or current_user.get("id") or "1")
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
    
    # Return default models if provider not found
    default_models = ["default-model-1", "default-model-2"]
    models = provider_models.get(provider_id, default_models)
    
    return {"models": models}
