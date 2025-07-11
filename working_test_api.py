#!/usr/bin/env python3
"""
Minimal working API server for AI provider configuration testing
"""
from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel
from typing import Optional, Dict, Any
import uvicorn
import logging

# Configure logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

# Create FastAPI app
app = FastAPI(title="AI Provider Test Server", version="1.0.0")

# Add CORS
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# In-memory storage
configurations = {}

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
def root():
    return {"message": "AI Provider Test Server", "status": "running"}

@app.get("/api/v1/ai-providers")
def get_providers():
    openai_config = configurations.get("openai", {})
    providers = [{
        "name": "OpenAI",
        "id": "openai",
        "logo": "/ai-providers/openai.svg",
        "apiKey": openai_config.get("apiKey", "").replace(openai_config.get("apiKey", ""), "••••••••••••••••") if openai_config.get("apiKey") else None,
        "isConfigured": "openai" in configurations,
        "modelOptions": ["dall-e-3", "dall-e-2"],
        "selectedModel": openai_config.get("selectedModel", "dall-e-3"),
        "maxTokens": 4096,
        "temperature": 0.7,
        "isActive": openai_config.get("isActive", True),
        "quality": openai_config.get("quality", "standard"),
        "size": openai_config.get("size", "1024x1024"),
        "style": openai_config.get("style", "vivid")
    }]
    logger.info(f"GET /api/v1/ai-providers - returning {len(providers)} providers")
    return providers

@app.post("/api/v1/ai-providers")
def create_provider(config: ProviderConfig):
    logger.info(f"POST /api/v1/ai-providers - creating config for {config.id}")
    configurations[config.id] = config.dict()
    logger.info(f"Stored configuration: {configurations}")
    
    # Return masked response
    response = config.dict()
    if response.get("apiKey"):
        response["apiKey"] = "••••••••••••••••"
    return response

@app.put("/api/v1/ai-providers/{provider_id}")
def update_provider(provider_id: str, config: ProviderConfig):
    logger.info(f"PUT /api/v1/ai-providers/{provider_id} - updating config")
    configurations[provider_id] = config.dict()
    logger.info(f"Updated configuration: {configurations}")
    
    # Return masked response
    response = config.dict()
    if response.get("apiKey"):
        response["apiKey"] = "••••••••••••••••"
    return response

@app.post("/api/v1/ai-providers/validate")
def validate_provider(data: dict):
    logger.info(f"POST /api/v1/ai-providers/validate - validating {data}")
    return {"valid": True, "message": "Configuration validated successfully"}

if __name__ == "__main__":
    logger.info("Starting AI Provider Test Server on port 8089...")
    uvicorn.run(app, host="127.0.0.1", port=8089, log_level="info")
