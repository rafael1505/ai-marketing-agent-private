#!/usr/bin/env python3
"""
Minimal API server to fix the OpenAI configuration form issue
"""
from fastapi import FastAPI, Request, Body, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel
from typing import Optional, Dict, Any
import uvicorn
import logging
import json
import os

# Configure logging
logging.basicConfig(level=logging.DEBUG, format='%(asctime)s - %(name)s - %(levelname)s - %(message)s')
logger = logging.getLogger(__name__)

# Create a simple FastAPI app
app = FastAPI(title="AI Provider Configuration Fix", version="1.0.0")

# Add CORS
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Add middleware to log all requests
@app.middleware("http")
async def log_requests(request: Request, call_next):
    logger.info(f"REQUEST: {request.method} {request.url}")
    response = await call_next(request)
    logger.info(f"RESPONSE: {response.status_code}")
    return response

# Simple in-memory storage for configurations
configurations = {}

# Models
class ProviderConfig(BaseModel):
    id: str
    name: str
    apiKey: Optional[str] = None
    selectedModel: Optional[str] = None
    quality: Optional[str] = None
    size: Optional[str] = None
    style: Optional[str] = None
    isActive: Optional[bool] = True
    customOptions: Optional[Dict[str, Any]] = None

@app.get("/")
async def root():
    return {"message": "AI Provider Test Server", "status": "running"}

# Add routes to handle duplicated path issue
@app.get("/api/v1/api/v1/ai-providers")
async def get_providers_duplicated_path():
    logger.info("Handling request with duplicated path prefix")
    return await get_providers()

@app.post("/api/v1/api/v1/ai-providers")
async def create_provider_duplicated_path(config: ProviderConfig):
    logger.info("Handling POST request with duplicated path prefix")
    return await create_provider(config)

@app.put("/api/v1/api/v1/ai-providers/{provider_id}")
async def update_provider_duplicated_path(provider_id: str, config: ProviderConfig):
    logger.info("Handling PUT request with duplicated path prefix")
    return await update_provider(provider_id, config)

@app.post("/api/v1/api/v1/ai-providers/validate")
async def validate_provider_duplicated_path(request: Request):
    logger.info("Handling validation request with duplicated path prefix")
    return await validate_provider(request)

@app.get("/api/v1/ai-providers")
async def get_providers():
    # Mock data - similar to what the main API returns
    providers = []
    
    # Add OpenAI provider with configuration if it exists
    openai_config = configurations.get("openai", {})
    providers.append({
        "name": "OpenAI",
        "id": "openai",
        "logo": "/ai-providers/openai.svg",
        "apiKey": openai_config.get("apiKey") and "••••••••••••••••",
        "isConfigured": "openai" in configurations and bool(openai_config.get("apiKey")),
        "modelOptions": ["dall-e-3", "dall-e-2"],
        "selectedModel": openai_config.get("selectedModel", "dall-e-3"),
        "maxTokens": openai_config.get("maxTokens", 4096),
        "temperature": openai_config.get("temperature", 0.7),
        "isActive": openai_config.get("isActive", False),  # Default to False unless explicitly set
        "available": True,  # This provider is available via API
        "configured": "openai" in configurations and bool(openai_config.get("apiKey")),
        "model": "dall-e-3",  # For compatibility
        "max_variations": 1,
        "supported_sizes": ["1024x1024", "1024x1792", "1792x1024"],
        "quality": openai_config.get("quality", "standard"),
        "size": openai_config.get("size", "1024x1024"),
        "style": openai_config.get("style", "vivid"),
        "customOptions": openai_config.get("customOptions", {}),
        "pricing": {"tier": "paid", "description": "Pay per image"}
    })
    
    # Add Stability AI provider (not configured by default)
    stability_config = configurations.get("stability", {})
    providers.append({
        "name": "Stability AI",
        "id": "stability",
        "logo": "/ai-providers/stability.svg",
        "apiKey": stability_config.get("apiKey") and "••••••••••••••••",
        "isConfigured": "stability" in configurations and bool(stability_config.get("apiKey")),
        "modelOptions": ["stable-diffusion-xl-1024-v1-0", "stable-diffusion-v1-6"],
        "selectedModel": stability_config.get("selectedModel", "stable-diffusion-xl-1024-v1-0"),
        "maxTokens": stability_config.get("maxTokens", 1000),
        "temperature": stability_config.get("temperature", 0.7),
        "isActive": stability_config.get("isActive", False),
        "available": True,
        "configured": "stability" in configurations and bool(stability_config.get("apiKey")),
        "model": "stable-diffusion-xl-1024-v1-0",
        "max_variations": 4,
        "supported_sizes": ["1024x1024", "1152x896", "896x1152"],
        "customOptions": stability_config.get("customOptions", {}),
        "pricing": {"tier": "paid", "description": "Pay per image"}
    })
    
    logger.info(f"Returning providers: {providers}")
    return providers

@app.post("/api/v1/ai-providers")
async def create_provider(config: ProviderConfig):
    logger.info(f"Creating provider config for {config.id}: {config.dict()}")
    
    # Check if we're receiving a masked API key (which shouldn't happen for creation)
    if config.apiKey and "••••" in config.apiKey:
        logger.warning(f"Received masked API key for creation of {config.id}")
        # For creation, we need a real API key, so reject masked keys
        raise HTTPException(status_code=400, detail="Cannot create configuration with masked API key")
    
    # Store in the configurations dictionary
    configurations[config.id] = config.dict()
    
    # Log the current state of configurations after creation
    logger.info(f"Current configurations after creation: {configurations}")
    
    # Return the created config with masked API key
    masked_config = {**config.dict()}
    if masked_config.get("apiKey"):
        masked_config["apiKey"] = "••••••••••••••••"
    
    return masked_config

@app.put("/api/v1/ai-providers/{provider_id}")
async def update_provider(provider_id: str, config: ProviderConfig):
    logger.info(f"Updating provider config for {provider_id}: {config.dict()}")
    
    # Get existing configuration if it exists
    existing_config = configurations.get(provider_id, {})
    
    # Merge with new config, preserving existing API key if not provided or if masked
    updated_config = {**existing_config, **config.dict(exclude_unset=True)}
    
    # If the API key in the update request is masked, keep the existing real API key
    if config.apiKey and "••••" in config.apiKey and existing_config.get("apiKey"):
        logger.info(f"Preserving existing API key for {provider_id} (received masked key)")
        updated_config["apiKey"] = existing_config["apiKey"]
    elif config.apiKey is None and existing_config.get("apiKey"):
        # If no API key is provided in the update, keep the existing one
        updated_config["apiKey"] = existing_config["apiKey"]
    
    # Store the updated configuration
    configurations[provider_id] = updated_config
    
    # Log the current state of configurations after update
    logger.info(f"Current configurations: {configurations}")
    
    # Return the updated config with masked API key
    masked_config = {**updated_config}
    if masked_config.get("apiKey"):
        masked_config["apiKey"] = "••••••••••••••••"
    
    return masked_config

@app.post("/api/v1/ai-providers/validate")
async def validate_provider(request: Request):
    data = await request.json()
    logger.info(f"Validating provider config: {data}")
    
    provider_id = data.get("providerId")
    api_key = data.get("apiKey")
    
    # If the API key appears to be masked, reject the validation
    if api_key and "••••" in api_key:
        logger.warning(f"Received masked API key for validation of {provider_id}")
        return {"valid": False, "message": "Cannot validate with masked API key"}
    
    # Basic validation - check that we have a provider_id and api_key
    if not provider_id or not api_key:
        return {"valid": False, "message": "Missing provider ID or API key"}
    
    # For this test API, we'll accept any non-masked API key
    logger.info(f"Validation successful for {provider_id}")
    return {"valid": True, "message": "Configuration validated successfully"}

# Add routes without /api/v1 prefix for direct frontend access
@app.get("/ai-providers")
async def get_providers_direct():
    logger.info("Handling direct GET request to /ai-providers")
    return await get_providers()

@app.post("/ai-providers")
async def create_provider_direct(config: ProviderConfig):
    logger.info("Handling direct POST request to /ai-providers")
    return await create_provider(config)

@app.put("/ai-providers/{provider_id}")
async def update_provider_direct(provider_id: str, config: ProviderConfig):
    logger.info("Handling direct PUT request to /ai-providers")
    return await update_provider(provider_id, config)

@app.post("/ai-providers/validate")
async def validate_provider_direct(request: Request):
    logger.info("Handling direct validation request to /ai-providers/validate")
    return await validate_provider(request)

# Add configurations endpoint that frontend expects
@app.get("/ai-providers/configurations")
async def get_provider_configurations():
    logger.info("Getting provider configurations")
    configs = []
    for provider_id, config in configurations.items():
        masked_config = {**config}
        if masked_config.get("apiKey"):
            masked_config["apiKey"] = "••••••••••••••••"
        configs.append(masked_config)
    return configs

# Add the same endpoint with /api/v1 prefix for consistency
@app.get("/api/v1/ai-providers/configurations")
async def get_provider_configurations_v1():
    logger.info("Getting provider configurations via /api/v1")
    return await get_provider_configurations()

# Add the fallback endpoint that the frontend expects
@app.get("/providers")
async def get_providers_fallback():
    logger.info("Handling fallback request to /providers")
    providers = await get_providers()
    return {"providers": providers}

# Add the main API endpoint that the frontend tries first (for port 8088)
@app.get("/api/v1/ai/providers")
async def get_providers_main_api():
    logger.info("Handling main API request to /api/v1/ai/providers")
    providers = await get_providers()
    return {"providers": providers}

# Add image generation endpoints for testing
@app.post("/api/v1/ai/generate-image")
async def generate_image_main_api(request: Request):
    logger.info("Handling image generation request via main API")
    return await generate_image_test(request)

@app.post("/generate")
async def generate_image_test(request: Request):
    data = await request.json()
    logger.info(f"Generating test image with data: {data}")
    
    prompt = data.get("prompt", "test image")
    provider = data.get("provider", "openai")
    size = data.get("size", "1024x1024")
    variations = data.get("variations", 1)
    style = data.get("style", "vivid")
    quality = data.get("quality", "standard")
    requested_model = data.get("model")  # Model requested from frontend
    
    # Check if the provider is configured and active
    provider_config = configurations.get(provider, {})
    if not provider_config.get("apiKey"):
        return {
            "success": False,
            "error": f"Provider {provider} is not configured with an API key",
            "model": "unknown"
        }
    
    if not provider_config.get("isActive", False):
        return {
            "success": False,
            "error": f"Provider {provider} is not active",
            "model": "unknown"
        }
    
    # Use the model from the request, or fall back to provider config, or default
    actual_model = (
        requested_model or 
        provider_config.get("selectedModel") or 
        "dall-e-3"
    )
    
    # Calculate mock cost based on model and variations
    cost_per_image = {
        "dall-e-3": 0.04 if quality == "standard" else 0.08,
        "dall-e-2": 0.02,
        "stable-diffusion-xl-1024-v1-0": 0.01,
        "stable-diffusion-v1-6": 0.008,
    }.get(actual_model, 0.04)
    
    total_cost = cost_per_image * variations
    
    # Return a mock successful response
    images = []
    for i in range(variations):
        # Generate a simple SVG placeholder image (for demo/testing purposes only)
        svg_content = f"""<svg width="512" height="512" xmlns="http://www.w3.org/2000/svg">
            <rect width="100%" height="100%" fill="#f0f0f0"/>
            <text x="50%" y="30%" text-anchor="middle" dy="0.3em" font-family="Arial" font-size="14">
                Test Image {i+1} (Demo Only)
            </text>
            <text x="50%" y="40%" text-anchor="middle" dy="0.3em" font-family="Arial" font-size="12">
                Provider: {provider}
            </text>
            <text x="50%" y="50%" text-anchor="middle" dy="0.3em" font-family="Arial" font-size="12">
                Model: {actual_model}
            </text>
            <text x="50%" y="60%" text-anchor="middle" dy="0.3em" font-family="Arial" font-size="12">
                Style: {style} | Quality: {quality}
            </text>
            <text x="50%" y="70%" text-anchor="middle" dy="0.3em" font-family="Arial" font-size="10">
                Prompt: {prompt[:40]}{'...' if len(prompt) > 40 else ''}
            </text>
        </svg>"""
        
        # Convert to data URL
        import base64
        svg_b64 = base64.b64encode(svg_content.encode()).decode()
        data_url = f"data:image/svg+xml;base64,{svg_b64}"
        images.append(data_url)
    
    return {
        "success": True,
        "images": images,
        "provider": provider,
        "model": actual_model,  # Return the actual model used
        "metadata": {
            "prompt": prompt,
            "size": size,
            "variations": variations,
            "style": style,
            "quality": quality,
            "note": "This is a demo/test API. SVG placeholders are used instead of real AI-generated images."
        },
        "cost": round(total_cost, 4),  # Mock cost calculation based on model and quality
        "error": None
    }

if __name__ == "__main__":
    logger.info("Starting minimal API server...")
    uvicorn.run(app, host="127.0.0.1", port=8089, reload=False)
