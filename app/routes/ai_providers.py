from typing import List, Optional
from fastapi import APIRouter, Depends, HTTPException, Body
from pydantic import BaseModel
from app.services.auth import get_current_user

router = APIRouter()

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

# Fake in-memory storage - in production, this would use a database
ai_providers_db = {}

@router.get("/api/v1/ai-providers", response_model=List[AIProviderModel])
def get_user_ai_providers(current_user_id: str = Depends(get_current_user)):
    """Get all AI providers configured for the current user"""
    if current_user_id not in ai_providers_db:
        return []
    
    # Don't return API keys in the list view
    providers = []
    for provider in ai_providers_db[current_user_id]:
        provider_copy = provider.copy()
        if "apiKey" in provider_copy:
            provider_copy["apiKey"] = "••••••••••••••••"
        providers.append(provider_copy)
    
    return providers

@router.get("/api/v1/ai-providers/{provider_id}", response_model=AIProviderModel)
def get_ai_provider(provider_id: str, current_user_id: str = Depends(get_current_user)):
    """Get a specific AI provider by ID"""
    if current_user_id not in ai_providers_db:
        raise HTTPException(status_code=404, detail="Provider not found")
    
    for provider in ai_providers_db[current_user_id]:
        if provider["id"] == provider_id:
            # Mask the API key
            provider_copy = provider.copy()
            if "apiKey" in provider_copy:
                provider_copy["apiKey"] = "••••••••••••••••"
            return provider_copy
    
    raise HTTPException(status_code=404, detail="Provider not found")

@router.post("/api/v1/ai-providers", response_model=AIProviderModel)
def create_ai_provider(provider: AIProviderModel, current_user_id: str = Depends(get_current_user)):
    """Create a new AI provider configuration"""
    if current_user_id not in ai_providers_db:
        ai_providers_db[current_user_id] = []
    
    # Check if provider with this ID already exists
    for existing in ai_providers_db[current_user_id]:
        if existing["id"] == provider.id:
            raise HTTPException(status_code=400, detail="Provider with this ID already exists")
    
    # Convert model to dict
    provider_dict = provider.dict()
    
    # Add to database
    ai_providers_db[current_user_id].append(provider_dict)
    
    # Return the created provider (without the API key)
    provider_copy = provider_dict.copy()
    if "apiKey" in provider_copy:
        provider_copy["apiKey"] = "••••••••••••••••"
    
    return provider_copy

@router.put("/api/v1/ai-providers/{provider_id}", response_model=AIProviderModel)
def update_ai_provider(
    provider_id: str, 
    updates: dict = Body(...), 
    current_user_id: str = Depends(get_current_user)
):
    """Update an existing AI provider configuration"""
    if current_user_id not in ai_providers_db:
        raise HTTPException(status_code=404, detail="Provider not found")
    
    for i, provider in enumerate(ai_providers_db[current_user_id]):
        if provider["id"] == provider_id:
            # Update the provider
            ai_providers_db[current_user_id][i].update(updates)
            
            # Return the updated provider (without the API key)
            provider_copy = ai_providers_db[current_user_id][i].copy()
            if "apiKey" in provider_copy:
                provider_copy["apiKey"] = "••••••••••••••••"
            
            return provider_copy
    
    raise HTTPException(status_code=404, detail="Provider not found")

@router.delete("/api/v1/ai-providers/{provider_id}")
def delete_ai_provider(provider_id: str, current_user_id: str = Depends(get_current_user)):
    """Delete an AI provider configuration"""
    if current_user_id not in ai_providers_db:
        raise HTTPException(status_code=404, detail="Provider not found")
    
    initial_count = len(ai_providers_db[current_user_id])
    ai_providers_db[current_user_id] = [
        p for p in ai_providers_db[current_user_id] if p["id"] != provider_id
    ]
    
    if len(ai_providers_db[current_user_id]) == initial_count:
        raise HTTPException(status_code=404, detail="Provider not found")
    
    return {"success": True}

@router.post("/api/v1/ai-providers/validate")
def validate_api_key(validation: ValidationRequest, current_user_id: str = Depends(get_current_user)):
    """Validate an API key for a provider"""
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
def get_provider_options(provider_id: str, current_user_id: str = Depends(get_current_user)):
    """Get available options for a provider (models, sizes, etc)"""
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
