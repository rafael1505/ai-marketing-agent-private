#!/usr/bin/env python3
"""
Minimal AI Provider Test Server
Tests the new AI provider system with a simple FastAPI server
"""
from fastapi import FastAPI, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel
from typing import Optional
import uvicorn
import sys
import os

# Add the current directory to path for imports
sys.path.insert(0, os.getcwd())

# Import the AI provider manager
from app.ai_providers.provider_manager import ai_provider_manager, ImageGenerationRequest

app = FastAPI(title="AI Provider Test Server", version="1.0.0")

# Add CORS middleware
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

class ImageRequest(BaseModel):
    prompt: str
    provider: str = "free-test-provider"
    size: str = "1024x1024"
    variations: int = 1

@app.get("/")
async def root():
    """Root endpoint"""
    return {"message": "AI Provider Test Server", "status": "running"}

@app.get("/providers")
async def list_providers():
    """List available AI providers"""
    try:
        status = ai_provider_manager.get_provider_status()
        return {
            "success": True,
            "providers": [
                {
                    "id": provider_id,
                    "name": info["name"],
                    "configured": info["configured"],
                    "available": info["available"],
                    "model": info["model"],
                    "max_variations": info["max_variations"]
                }
                for provider_id, info in status.items()
            ]
        }
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@app.post("/generate")
async def generate_image(request: ImageRequest):
    """Generate image using specified provider"""
    try:
        # Create internal request object
        gen_request = ImageGenerationRequest(
            prompt=request.prompt,
            size=request.size,
            variations=request.variations
        )
        
        # Generate image
        result = await ai_provider_manager.generate_image(request.provider, gen_request)
        
        if result.success:
            return {
                "success": True,
                "images": result.images,
                "provider": result.provider,
                "model": result.model,
                "metadata": result.metadata,
                "cost": result.cost
            }
        else:
            raise HTTPException(status_code=500, detail=result.error)
            
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@app.get("/test")
async def test_generation():
    """Test endpoint for quick verification"""
    try:
        request = ImageGenerationRequest(
            prompt="Test image generation",
            size="512x512",
            variations=2
        )
        
        result = await ai_provider_manager.generate_image("free-test-provider", request)
        
        return {
            "test": "success",
            "generated_images": len(result.images),
            "provider": result.provider,
            "images": result.images[:2]  # Show first 2 images
        }
    except Exception as e:
        return {"test": "failed", "error": str(e)}

if __name__ == "__main__":
    print("🚀 Starting AI Provider Test Server...")
    print("📊 Available endpoints:")
    print("   GET  /           - Root endpoint")
    print("   GET  /providers  - List providers")
    print("   POST /generate   - Generate images")
    print("   GET  /test       - Quick test")
    print("🌐 Server will be available at: http://127.0.0.1:8089")
    
    uvicorn.run(app, host="127.0.0.1", port=8089, log_level="info")
