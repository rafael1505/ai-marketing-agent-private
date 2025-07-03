"""
Image generation endpoint using free AI providers
"""
from fastapi import APIRouter, Depends, HTTPException, Query
from typing import Annotated, Dict, Any
from app.ai_providers.free_provider import free_provider

router = APIRouter()

@router.post("/generate-image")
async def generate_image_with_free_provider(
    prompt: Annotated[str, Query()],
    ai_provider: Annotated[str, Query()] = "free-test-provider",
    size: Annotated[str, Query()] = "1024x1024",
    style: Annotated[str, Query()] = "photorealistic"
) -> Dict[str, Any]:
    """Generate an image using the free test provider"""
    
    if ai_provider == "free-test-provider":
        try:
            result = free_provider.generate_image(
                prompt=prompt,
                size=size,
                style=style
            )
            return {
                "success": True,
                "image_url": result["url"],
                "prompt": prompt,
                "provider": ai_provider,
                "metadata": result.get("metadata", {})
            }
        except Exception as e:
            raise HTTPException(status_code=500, detail=f"Image generation failed: {str(e)}")
    else:
        raise HTTPException(status_code=400, detail=f"Provider '{ai_provider}' not supported")

@router.get("/providers")
async def list_available_providers() -> Dict[str, Any]:
    """List available AI providers"""
    return {
        "providers": [
            {
                "id": "free-test-provider",
                "name": "Free Test Provider",
                "configured": True,
                "available": True,
                "features": ["image_generation"],
                "description": "Free placeholder image generator for testing"
            }
        ]
    }
