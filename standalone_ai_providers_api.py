from fastapi import FastAPI, HTTPException
from pydantic import BaseModel
from typing import List, Optional
import uvicorn

app = FastAPI(title="Standalone AI Provider API")

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

# Mock data store
mock_providers = [
    {
        "name": "Stability AI",
        "id": "stability",
        "logo": "/ai-providers/stability.svg",
        "isConfigured": True,
        "selectedModel": "stable-diffusion-xl-1024-v1-0",
        "maxTokens": 1000,
        "temperature": 0.7,
        "isActive": True
    },
    {
        "name": "Hugging Face",
        "id": "huggingface",
        "logo": "/ai-providers/huggingface.svg",
        "isConfigured": False
    }
]

@app.get("/api/v1/ai-providers", response_model=List[AIProviderModel])
async def get_providers():
    """Get all AI providers"""
    return mock_providers

@app.get("/api/v1/ai-providers/{provider_id}", response_model=AIProviderModel)
async def get_provider(provider_id: str):
    """Get a specific AI provider by ID"""
    provider = next((p for p in mock_providers if p["id"] == provider_id), None)
    if not provider:
        raise HTTPException(status_code=404, detail="Provider not found")
    return provider

@app.post("/api/v1/ai-providers", response_model=AIProviderModel)
async def create_provider(provider: AIProviderModel):
    """Create a new AI provider"""
    # Check if provider already exists
    existing = next((p for p in mock_providers if p["id"] == provider.id), None)
    if existing:
        raise HTTPException(status_code=400, detail="Provider with this ID already exists")
    
    # Add to mock data
    new_provider = provider.dict()
    mock_providers.append(new_provider)
    
    return new_provider

@app.put("/api/v1/ai-providers/{provider_id}", response_model=AIProviderModel)
async def update_provider(provider_id: str, updates: dict):
    """Update an existing AI provider"""
    # Find provider
    provider_index = next((i for i, p in enumerate(mock_providers) if p["id"] == provider_id), None)
    if provider_index is None:
        raise HTTPException(status_code=404, detail="Provider not found")
    
    # Update provider
    for key, value in updates.items():
        mock_providers[provider_index][key] = value
    
    return mock_providers[provider_index]

@app.delete("/api/v1/ai-providers/{provider_id}")
async def delete_provider(provider_id: str):
    """Delete an AI provider"""
    # Find provider
    provider_index = next((i for i, p in enumerate(mock_providers) if p["id"] == provider_id), None)
    if provider_index is None:
        raise HTTPException(status_code=404, detail="Provider not found")
    
    # Delete provider
    del mock_providers[provider_index]
    
    return {"success": True}

@app.post("/api/v1/ai-providers/validate")
async def validate_api_key(validation: ValidationRequest):
    """Validate an API key for a provider"""
    # This is a mock implementation
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

@app.get("/api/v1/ai-providers/{provider_id}/options")
async def get_provider_options(provider_id: str):
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

@app.get("/")
async def root():
    """Root endpoint"""
    return {
        "app": "Standalone AI Provider API",
        "endpoints": [
            "/api/v1/ai-providers",
            "/api/v1/ai-providers/{provider_id}",
            "/api/v1/ai-providers/{provider_id}/options",
            "/api/v1/ai-providers/validate"
        ]
    }

if __name__ == "__main__":
    uvicorn.run(app, host="127.0.0.1", port=8096)
