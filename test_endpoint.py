from typing import Any, List, Optional, Annotated
from datetime import datetime
from fastapi import APIRouter, Depends, HTTPException, File, UploadFile, Request, Query
from motor.motor_asyncio import AsyncIOMotorClient

# Temporary test endpoint without authentication
router = APIRouter()

@router.post("/test-materials/{material_id}/images")
async def test_add_generated_image(
    material_id: str,
    url: Annotated[str, Query()],
    prompt: Annotated[str, Query()],
    ai_provider: Annotated[str, Query()],
    generation_params: Annotated[str, Query()],  # Will be JSON string from query param
    request: Request
) -> Any:
    # Parse the generation_params JSON string
    import json
    try:
        parsed_params = json.loads(generation_params)
    except json.JSONDecodeError:
        parsed_params = {}
    
    # Return a mock response
    return {
        "id": material_id,
        "message": "Test endpoint working",
        "received_data": {
            "url": url,
            "prompt": prompt,
            "ai_provider": ai_provider,
            "generation_params": parsed_params
        }
    }
