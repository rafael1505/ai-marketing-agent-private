"""
Image generation routes — thin delegation layer (ARCH-LAYER-001).

Pattern per handler:
  cid = _cid(request)               # extract or generate correlation ID
  db  = request.app.mongodb
  return await ai_generation_service.method(db, ..., correlation_id=cid)
"""
import uuid
from typing import Annotated, Dict, Any, Optional, List
from fastapi import APIRouter, Request, Query
from pydantic import BaseModel

import app.services.ai_generation_service as ai_generation_service

router = APIRouter()


class ImageGenerationRequestBody(BaseModel):
    """Request body for POST /generate-image."""
    prompt: str
    ai_provider: str = "free-test-provider"
    size: str = "1024x1024"
    style: str = "photorealistic"
    quality: str = "standard"
    variations: int = 1
    negative_prompt: Optional[str] = None
    seed: Optional[int] = None
    people_preference: str = "auto"


def _cid(request: Request) -> str:
    """Extract X-Correlation-ID from headers, or generate a fresh UUID."""
    return request.headers.get("X-Correlation-ID") or str(uuid.uuid4())


@router.post("/generate-image")
async def generate_image_with_provider(
    request: Request,
    request_body: ImageGenerationRequestBody,
) -> Dict[str, Any]:
    """Generate one or more images using the specified AI provider."""
    db = request.app.mongodb
    return await ai_generation_service.generate_image(
        db=db,
        provider_id=request_body.ai_provider,
        prompt=request_body.prompt,
        size=request_body.size,
        style=request_body.style,
        quality=request_body.quality,
        variations=request_body.variations,
        negative_prompt=request_body.negative_prompt,
        seed=request_body.seed,
        people_preference=request_body.people_preference,
        correlation_id=_cid(request),
    )


@router.post("/generate-image-multi")
async def generate_multiple_images(
    request: Request,
    prompt: Annotated[str, Query()],
    ai_provider: Annotated[str, Query()] = "free-test-provider",
    size: Annotated[str, Query()] = "1024x1024",
    style: Annotated[str, Query()] = "photorealistic",
    variations: Annotated[int, Query()] = 5,
) -> Dict[str, Any]:
    """Backward-compatibility endpoint for multiple image variations."""
    db = request.app.mongodb
    return await ai_generation_service.generate_image(
        db=db,
        provider_id=ai_provider,
        prompt=prompt,
        size=size,
        style=style,
        variations=variations,
        correlation_id=_cid(request),
    )


@router.get("/providers")
async def list_available_providers(request: Request) -> Dict[str, Any]:
    """List all registered providers with status and capabilities."""
    return await ai_generation_service.get_available_providers(request.app.mongodb)


@router.get("/providers/recommended")
async def get_recommended_provider(
    request: Request,
    features: Annotated[List[str], Query()] = None,
) -> Dict[str, Any]:
    """Return the recommended provider for the given feature requirements."""
    return await ai_generation_service.get_recommended_provider(
        db=request.app.mongodb,
        features=features,
        correlation_id=_cid(request),
    )
