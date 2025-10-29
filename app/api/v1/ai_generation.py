"""
Image generation endpoint using multiple AI providers
"""
from fastapi import APIRouter, Depends, HTTPException, Query, Body, Request
from typing import Annotated, Dict, Any, Optional, List
from pydantic import BaseModel
from app.ai_providers.provider_manager import get_provider_manager, ImageGenerationRequest
import logging
import traceback

router = APIRouter()
logger = logging.getLogger(__name__)

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
    request: Request,
    request_body: ImageGenerationRequestBody
) -> Dict[str, Any]:
    """Generate an image using the specified AI provider"""
    
    # Get provider manager with database connection
    manager = get_provider_manager(database_client=getattr(request.app, 'mongodb', None))
    
    # Refresh provider configs from database to get latest API keys
    await manager.refresh_provider_configs()
    
    # Create internal request object
    generation_request = ImageGenerationRequest(
        prompt=request_body.prompt,
        size=request_body.size,
        style=request_body.style,
        quality=request_body.quality,
        variations=request_body.variations,
        negative_prompt=request_body.negative_prompt,
        seed=request_body.seed
    )
    
    try:
        logger.info(f"Generating image with provider: {request_body.ai_provider}, variations: {request_body.variations}")
        result = await manager.generate_image(request_body.ai_provider, generation_request)
        
        if result.success:
            logger.info(f"Image generation successful: {len(result.images)} images generated")
            
            # Log image URL details
            for i, img_url in enumerate(result.images):
                logger.info(f"Image {i+1} URL length: {len(img_url)} characters")
                logger.info(f"Image {i+1} URL preview: {img_url[:100]}...")
            
            response_data = {
                "success": True,
                "images": result.images,
                "prompt": request_body.prompt,
                "provider": result.provider,
                "model": result.model,
                "metadata": result.metadata,
                "cost": result.cost
            }
            logger.info(f"Returning response with {len(result.images)} images")
            logger.info(f"Total response size estimate: {len(str(response_data))} characters")
            
            try:
                import json
                json_response = json.dumps(response_data)
                logger.info(f"Response successfully serialized to JSON: {len(json_response)} bytes")
                return response_data
            except Exception as json_error:
                logger.error(f"Failed to serialize response to JSON: {json_error}")
                raise
        else:
            # Return enriched error details if available
            logger.error(f"Image generation failed: {result.error}")
            if result.error_details:
                return {
                    "success": False,
                    "error": result.error,
                    "error_details": result.error_details,
                    "provider": result.provider
                }
            else:
                # Fallback to simple error
                raise HTTPException(status_code=500, detail=result.error)
            
    except HTTPException:
        # Re-raise HTTP exceptions
        logger.error("HTTPException occurred during image generation")
        raise
    except Exception as e:
        # Log the full exception with traceback
        logger.error(f"Unexpected error in image generation: {str(e)}")
        logger.error(f"Error type: {type(e).__name__}")
        logger.error(f"Traceback: {traceback.format_exc()}")
        raise HTTPException(status_code=500, detail=f"Image generation failed: {str(e)}")

@router.post("/generate-image-multi")
async def generate_multiple_images(
    request: Request,
    prompt: Annotated[str, Query()],
    ai_provider: Annotated[str, Query()] = "free-test-provider",
    size: Annotated[str, Query()] = "1024x1024",
    style: Annotated[str, Query()] = "photorealistic",
    variations: Annotated[int, Query()] = 5
) -> Dict[str, Any]:
    """Generate multiple image variations (backward compatibility endpoint)"""
    
    # Get provider manager with database connection
    manager = get_provider_manager(database_client=getattr(request.app, 'mongodb', None))
    
    # Refresh provider configs from database
    await manager.refresh_provider_configs()
    
    generation_request = ImageGenerationRequest(
        prompt=prompt,
        size=size,
        style=style,
        variations=variations
    )
    
    try:
        result = await manager.generate_image(ai_provider, generation_request)
        
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
async def list_available_providers(request: Request) -> Dict[str, Any]:
    """List available AI providers with their status and capabilities"""
    try:
        # Get provider manager with database connection
        manager = get_provider_manager(database_client=getattr(request.app, 'mongodb', None))
        
        # Refresh provider configs from database
        await manager.refresh_provider_configs()
        
        provider_status = manager.get_provider_status()
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
    request: Request,
    features: Annotated[List[str], Query()] = None
) -> Dict[str, Any]:
    """Get recommended provider based on requirements"""
    try:
        # Get provider manager with database connection
        manager = get_provider_manager(database_client=getattr(request.app, 'mongodb', None))
        
        # Refresh provider configs from database
        await manager.refresh_provider_configs()
        
        recommended = manager.get_recommended_provider(features)
        provider_status = manager.get_provider_status()
        
        if recommended in provider_status:
            return {
                "provider_id": recommended,
                "name": provider_status[recommended]["name"],
                "reason": f"Best available provider for requested features",
                "status": provider_status[recommended]
            }
        else:
            return {
                "provider_id": "free-test-provider",
                "name": "Test Provider",
                "reason": "Fallback provider",
                "status": {}
            }
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

        provider_status = manager.get_provider_status()
