"""
Image generation endpoint using multiple AI providers
"""
from fastapi import APIRouter, Depends, HTTPException, Query, Body
from typing import Annotated, Dict, Any, Optional, List
from pydantic import BaseModel
from app.ai_providers.provider_manager import ai_provider_manager, ImageGenerationRequest

router = APIRouter()

class ImageGenerationRequestBody(BaseModel):
    prompt: str
    ai_provider: str = "free-test-provider"
    size: str = "1024x1024"
    style: str = "photorealistic"
    quality: str = "standard"
    variations: int = 1
    negative_prompt: Optional[str] = None
    seed: Optional[int] = None

@router.post("/generate-image")
async def generate_image_with_provider(
    request_body: ImageGenerationRequestBody
) -> Dict[str, Any]:
    """Generate an image using the specified AI provider"""
    
    # Create internal request object
    request = ImageGenerationRequest(
        prompt=request_body.prompt,
        size=request_body.size,
        style=request_body.style,
        quality=request_body.quality,
        variations=request_body.variations,
        negative_prompt=request_body.negative_prompt,
        seed=request_body.seed
    )
    
    try:
        result = await ai_provider_manager.generate_image(request_body.ai_provider, request)
        
        if result.success:
            return {
                "success": True,
                "images": result.images,
                "prompt": request_body.prompt,
                "provider": result.provider,
                "model": result.model,
                "metadata": result.metadata,
                "cost": result.cost
            }
        else:
            raise HTTPException(status_code=500, detail=result.error)
            
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Image generation failed: {str(e)}")

@router.post("/generate-image-multi")
async def generate_multiple_images(
    prompt: Annotated[str, Query()],
    ai_provider: Annotated[str, Query()] = "free-test-provider",
    size: Annotated[str, Query()] = "1024x1024",
    style: Annotated[str, Query()] = "photorealistic",
    variations: Annotated[int, Query()] = 5
) -> Dict[str, Any]:
    """Generate multiple image variations (backward compatibility endpoint)"""
    
    request = ImageGenerationRequest(
        prompt=prompt,
        size=size,
        style=style,
        variations=variations
    )
    
    try:
        result = await ai_provider_manager.generate_image(ai_provider, request)
        
        if result.success:
            return {
                "success": True,
                "images": result.images,
                "prompt": prompt,
                "provider": result.provider,
                "model": result.model,
                "metadata": result.metadata,
                "cost": result.cost
            }
        else:
            raise HTTPException(status_code=500, detail=result.error)
            
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Image generation failed: {str(e)}")

@router.get("/providers")
async def list_available_providers() -> Dict[str, Any]:
    """List available AI providers with their status and capabilities"""
    try:
        provider_status = ai_provider_manager.get_provider_status()
        return {
            "providers": [
                {
                    "id": provider_id,
                    "name": info["name"],
                    "configured": info["configured"],
                    "available": info["available"],
                    "model": info["model"],
                    "max_variations": info["max_variations"],
                    "supported_sizes": info["supported_sizes"],
                    "features": info["features"],
                    "pricing": info["pricing"],
                    "status": info["status"]
                }
                for provider_id, info in provider_status.items()
            ]
        }
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Failed to get provider status: {str(e)}")

@router.get("/providers/recommended")
async def get_recommended_provider(
    features: Annotated[Optional[List[str]], Query()] = None
) -> Dict[str, Any]:
    """Get recommended provider based on availability and features"""
    try:
        recommended = ai_provider_manager.get_recommended_provider(features)
        provider_status = ai_provider_manager.get_provider_status()
        
        if recommended in provider_status:
            return {
                "recommended_provider": recommended,
                "provider_info": provider_status[recommended]
            }
        else:
            raise HTTPException(status_code=500, detail="No available providers found")
            
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Failed to get recommended provider: {str(e)}")
