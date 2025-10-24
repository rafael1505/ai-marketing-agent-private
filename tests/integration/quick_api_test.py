#!/usr/bin/env python3
"""
Quick API test server to verify the proxy is working
Now with proper provider configuration persistence
"""

from fastapi import FastAPI, Request
from fastapi.middleware.cors import CORSMiddleware
import uvicorn
import time
import json
import os
from datetime import datetime
from typing import Dict, Any, List

app = FastAPI(title="Quick API Test")

# Add CORS middleware
app.add_middleware(
    CORSMiddleware,
    allow_origins=["http://localhost:3001", "http://127.0.0.1:3001"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Configuration storage file
CONFIG_FILE = "provider_configs.json"

# In-memory configuration storage
provider_configs: Dict[str, Dict[str, Any]] = {}

def load_configurations():
    """Load provider configurations from file"""
    global provider_configs
    try:
        if os.path.exists(CONFIG_FILE):
            with open(CONFIG_FILE, 'r') as f:
                provider_configs = json.load(f)
                print(f"[DEBUG] Loaded {len(provider_configs)} provider configurations from {CONFIG_FILE}")
        else:
            provider_configs = {}
            print(f"[DEBUG] No configuration file found, starting with empty configs")
    except Exception as e:
        print(f"[ERROR] Failed to load configurations: {e}")
        provider_configs = {}

def save_configurations():
    """Save provider configurations to file"""
    try:
        with open(CONFIG_FILE, 'w') as f:
            json.dump(provider_configs, f, indent=2)
        print(f"[DEBUG] Saved {len(provider_configs)} provider configurations to {CONFIG_FILE}")
    except Exception as e:
        print(f"[ERROR] Failed to save configurations: {e}")

# Load configurations on startup
load_configurations()

# Add request logging middleware with correlation ID support
@app.middleware("http")
async def log_requests(request: Request, call_next):
    start_time = time.time()
    correlation_id = request.headers.get('X-Correlation-ID', 'unknown')
    
    # Log request start
    print(f"[{datetime.now().isoformat()}] Request Start [{correlation_id}]: {request.method} {request.url}")
    
    response = await call_next(request)
    process_time = time.time() - start_time
    
    # Log request completion
    print(f"[{datetime.now().isoformat()}] Request Complete [{correlation_id}]: {request.method} {request.url} - Status: {response.status_code} - Time: {process_time:.3f}s")
    
    # Add correlation ID to response headers for debugging
    response.headers["X-Correlation-ID"] = correlation_id
    
    return response

# Mock provider data
MOCK_PROVIDERS = [
    {
        "id": "openai",
        "name": "OpenAI DALL-E",
        "type": "image",
        "status": "active",
        "description": "OpenAI DALL-E for content generation",
        "configured": False,
        "available": True,
        "model": "dall-e-3",
        "max_variations": 4,
        "supported_sizes": ["512x512", "1024x1024"],
        "features": ["text-to-image"],
        "pricing": {"per_image": 0.04}
    },
    {
        "id": "stability",
        "name": "Stability AI",
        "type": "image",
        "status": "inactive",
        "description": "Stability AI for content generation",
        "configured": False,
        "available": True,
        "model": "stable-diffusion-xl",
        "max_variations": 4,
        "supported_sizes": ["512x512", "768x768", "1024x1024"],
        "features": ["text-to-image"],
        "pricing": {"per_image": 0.03}
    },
    {
        "id": "test",
        "name": "Test Provider",
        "type": "text",
        "status": "active",
        "description": "Test Provider for content generation",
        "configured": True,
        "available": True,
        "model": "test-model",
        "max_variations": 2,
        "supported_sizes": ["any"],
        "features": ["text-generation"],
        "pricing": {"per_request": 0.00}
    },
    {
        "id": "midjourney",
        "name": "Midjourney",
        "type": "image",
        "status": "active",
        "description": "Midjourney for artistic content generation",
        "configured": False,
        "available": True,
        "model": "midjourney-v6",
        "max_variations": 4,
        "supported_sizes": ["1024x1024", "1792x1024"],
        "features": ["text-to-image", "artistic"],
        "pricing": {"per_image": 0.08}
    },
    {
        "id": "anthropic",
        "name": "Anthropic Claude",
        "type": "text",
        "status": "active",
        "description": "Anthropic Claude for text generation",
        "configured": False,
        "available": True,
        "model": "claude-3",
        "max_variations": 3,
        "supported_sizes": ["any"],
        "features": ["text-generation", "analysis"],
        "pricing": {"per_token": 0.00001}
    },
    {
        "id": "replicate",
        "name": "Replicate",
        "type": "image",
        "status": "active",
        "description": "Replicate for diverse AI models",
        "configured": False,
        "available": True,
        "model": "various",
        "max_variations": 4,
        "supported_sizes": ["512x512", "1024x1024"],
        "features": ["text-to-image", "model-variety"],
        "pricing": {"per_prediction": 0.05}
    },
    {
        "id": "huggingface",
        "name": "Hugging Face",
        "type": "text",
        "status": "active",
        "description": "Hugging Face for open-source models",
        "configured": False,
        "available": True,
        "model": "various-oss",
        "max_variations": 3,
        "supported_sizes": ["any"],
        "features": ["text-generation", "open-source"],
        "pricing": {"per_request": 0.001}
    },
    {
        "id": "google",
        "name": "Google Gemini",
        "type": "text",
        "status": "active",
        "description": "Google Gemini for advanced AI",
        "configured": False,
        "available": True,
        "model": "gemini-pro",
        "max_variations": 3,
        "supported_sizes": ["any"],
        "features": ["text-generation", "multimodal"],
        "pricing": {"per_token": 0.00002}
    },
    {
        "id": "cohere",
        "name": "Cohere",
        "type": "text",
        "status": "active",
        "description": "Cohere for enterprise AI",
        "configured": False,
        "available": True,
        "model": "command",
        "max_variations": 3,
        "supported_sizes": ["any"],
        "features": ["text-generation", "enterprise"],
        "pricing": {"per_token": 0.000015}
    }
]

@app.get("/")
async def root():
    return {"message": "Quick API Test Server is running"}

@app.get("/health")
async def health():
    return {"status": "ok"}

@app.get("/api/v1/ai-providers")
async def get_providers():
    """Get all providers with their current configurations"""
    print(f"[DEBUG] GET /api/v1/ai-providers called - Loaded {len(MOCK_PROVIDERS)} providers from mock data")
    
    # Create a copy of providers and merge with saved configurations
    providers_with_configs = []
    for provider in MOCK_PROVIDERS:
        provider_copy = provider.copy()
        provider_id = provider_copy["id"]
        
        # Check if we have saved configuration for this provider
        if provider_id in provider_configs:
            config = provider_configs[provider_id]
            # Mark as configured if it has an API key
            if config.get("apiKey"):
                provider_copy["configured"] = True
                # Add configured fields (without exposing real API key)
                provider_copy["apiKey"] = "••••••••••••••••"  # Mask the API key
                if "selectedModel" in config:
                    provider_copy["selectedModel"] = config["selectedModel"]
                if "isActive" in config:
                    provider_copy["isActive"] = config["isActive"]
            
        providers_with_configs.append(provider_copy)
    
    return providers_with_configs

@app.get("/diagnostic/ping")
async def diagnostic_ping():
    print(f"[DEBUG] GET /diagnostic/ping called")
    return {"status": "pong", "server": "quick-test-api"}

@app.get("/diagnostic/test-providers")
async def test_providers_simple():
    print(f"[DEBUG] GET /diagnostic/test-providers called")
    return {
        "status": "ok",
        "provider_count": len(MOCK_PROVIDERS),
        "sample_provider": MOCK_PROVIDERS[0] if MOCK_PROVIDERS else None
    }

@app.get("/api/v1/ai-providers/configurations")
async def get_provider_configurations():
    print("Getting provider configurations")
    return {"configurations": []}

@app.post("/api/v1/ai-providers")
async def save_provider_configuration(request: dict):
    """Save a new provider configuration"""
    print(f"Saving provider configuration: {request}")
    provider_id = request.get("id", "unknown")
    
    # Store the configuration
    provider_configs[provider_id] = request
    save_configurations()
    
    return {
        "success": True,
        "message": f"Provider {provider_id} configuration saved successfully",
        "provider": request
    }

@app.put("/api/v1/ai-providers/{provider_id}")
async def update_provider_configuration(provider_id: str, request: dict):
    """Update an existing provider configuration"""
    print(f"Updating provider {provider_id} configuration: {request}")
    
    # Store/update the configuration
    provider_configs[provider_id] = request
    save_configurations()
    
    return {
        "success": True,
        "message": f"Provider {provider_id} configuration updated successfully",
        "provider": request
    }

@app.post("/api/v1/ai-providers/validate")
async def validate_provider(request: dict):
    provider_id = request.get("providerId", "")
    api_key = request.get("apiKey", "")
    print(f"Validating API key for provider: {provider_id}")
    
    if provider_id == "openai":
        if not api_key or api_key == "test-key":
            return {
                "valid": False,
                "message": "Invalid API key. Please provide a valid OpenAI API key.",
                "error": {
                    "type": "invalid_api_key",
                    "correlation_id": "validate-openai-123",
                    "suggested_actions": ["Get a valid API key from OpenAI dashboard", "Check API key format"]
                }
            }
        else:
            return {
                "valid": True,
                "message": "OpenAI API key validated successfully!",
                "provider_info": {
                    "name": "OpenAI", 
                    "type": "image_generation",
                    "models": ["dall-e-3", "dall-e-2"]
                }
            }
    
    return {
        "valid": True,
        "message": f"Provider {provider_id} validated successfully",
        "provider_info": {"name": provider_id, "type": "test"}
    }

@app.post("/api/v1/ai-providers/test-connection")
async def test_provider_connection(request: dict):
    provider_id = request.get("providerId", "")
    api_key = request.get("apiKey", "")
    print(f"Testing connection for provider: {provider_id}")
    
    if provider_id == "openai":
        if api_key and len(api_key) > 10:
            return {
                "success": True,
                "message": "Connection successful! OpenAI API is reachable.",
                "response_time": "245ms",
                "status": "connected"
            }
        else:
            return {
                "success": False,
                "message": "Connection failed. Invalid or missing API key.",
                "error": "authentication_failed",
                "status": "disconnected"
            }
    
    return {
        "success": True,
        "message": f"Connection test successful for {provider_id}",
        "response_time": "120ms",
        "status": "connected"
    }

@app.get("/diagnostic/ping")
async def diagnostic_ping():
    return {"status": "pong", "server": "quick-test-api"}

@app.get("/api/v1/diagnostic/ping")
async def diagnostic_ping_v1():
    return {"status": "pong", "server": "quick-test-api-v1"}

if __name__ == "__main__":
    print("Starting Quick API Test Server on port 8088...")
    uvicorn.run(app, host="127.0.0.1", port=8088, log_level="info")