from typing import Any, List, Optional, Annotated
from datetime import datetime
from fastapi import APIRouter, Depends, HTTPException, File, UploadFile, Request, Query
from motor.motor_asyncio import AsyncIOMotorClient
from bson import ObjectId

from app.core.config import settings
from app.api.v1.deps import get_current_active_user
from app.core.db_utils import get_db_collection
from app.models.material import (
    MaterialCreate,
    MaterialUpdate,
    MaterialInDB,
    MaterialStage,
    MaterialStatus
)
from app.db.material import MaterialDB

router = APIRouter()

def serialize_material(material: dict) -> dict:
    """Convert MongoDB ObjectId to string for JSON serialization"""
    if material and "_id" in material:
        material["id"] = str(material["_id"])
        del material["_id"]
    return material

def serialize_materials(materials: list) -> list:
    """Convert list of MongoDB materials to JSON-serializable format"""
    return [serialize_material(mat.copy()) for mat in materials]

@router.post("")
async def create_material(
    material: MaterialCreate,
    current_user: Annotated[dict, Depends(get_current_active_user)],
    request: Request
) -> Any:
    mongodb = request.app.mongodb
    materials_collection = get_db_collection(mongodb, "materials")
    material_db = MaterialDB(materials_collection)
    created_material = await material_db.create_material(
        material,
        str(current_user["_id"]),
        current_user["company_id"]
    )
    # Convert ObjectId to string for JSON serialization
    return serialize_material(created_material)

@router.get("")
async def list_materials(
    current_user: Annotated[dict, Depends(get_current_active_user)],
    request: Request,
    stage: Optional[MaterialStage] = None,
    status: Optional[MaterialStatus] = None,
    skip: int = 0,
    limit: int = 100
) -> Any:
    mongodb = request.app.mongodb
    materials_collection = get_db_collection(mongodb, "materials")
    material_db = MaterialDB(materials_collection)
    
    # Print debug info
    print(f"list_materials called with company_id: {current_user['company_id']}")
    
    # Get materials for this company
    materials = await material_db.get_company_materials(
        current_user["company_id"],
        stage=stage,
        status=status,
        skip=skip,
        limit=limit
    )
    
    print(f"Found {len(materials)} materials")
    
    # Convert ObjectId to string for JSON serialization
    serialized_materials = serialize_materials(materials)
    
    # Return serialized materials
    return serialized_materials

@router.get("/{material_id}")
async def get_material(
    material_id: str,
    current_user: Annotated[dict, Depends(get_current_active_user)],
    request: Request
) -> Any:
    mongodb = request.app.mongodb
    materials_collection = get_db_collection(mongodb, "materials")
    material_db = MaterialDB(materials_collection)
    material = await material_db.get(material_id)
    if not material:
        raise HTTPException(status_code=404, detail="Material not found")
    if material["company_id"] != current_user["company_id"]:
        raise HTTPException(status_code=403, detail="Not enough permissions")
    # Convert ObjectId to string for JSON serialization
    return serialize_material(material)

@router.put("/{material_id}")
async def update_material(
    material_id: str,
    material: MaterialUpdate,
    current_user: Annotated[dict, Depends(get_current_active_user)],
    request: Request
) -> Any:
    mongodb = request.app.mongodb
    materials_collection = get_db_collection(mongodb, "materials")
    material_db = MaterialDB(materials_collection)
    current_material = await material_db.get(material_id)
    if not current_material:
        raise HTTPException(status_code=404, detail="Material not found")
    if current_material["company_id"] != current_user["company_id"]:
        raise HTTPException(status_code=403, detail="Not enough permissions")
    
    updated_material = await material_db.update(material_id, material.model_dump())
    if not updated_material:
        raise HTTPException(status_code=404, detail="Material not found")
    # Convert ObjectId to string for JSON serialization
    return serialize_material(updated_material)

@router.post("/{material_id}/images")
async def add_generated_image(
    material_id: str,
    url: Annotated[str, Query()],
    prompt: Annotated[str, Query()],
    ai_provider: Annotated[str, Query()],
    generation_params: Annotated[str, Query()],  # Will be JSON string from query param
    current_user: Annotated[dict, Depends(get_current_active_user)],
    request: Request
) -> Any:
    mongodb = request.app.mongodb
    materials_collection = get_db_collection(mongodb, "materials")
    material_db = MaterialDB(materials_collection)
    current_material = await material_db.get(material_id)
    if not current_material:
        raise HTTPException(status_code=404, detail="Material not found")
    if current_material["company_id"] != current_user["company_id"]:
        raise HTTPException(status_code=403, detail="Not enough permissions")
    
    # Parse the generation_params JSON string
    import json
    try:
        parsed_params = json.loads(generation_params)
    except json.JSONDecodeError:
        parsed_params = {}
    
    # If using the free test provider, generate the image
    if ai_provider == "free-test-provider":
        try:
            from app.ai_providers.free_provider import free_provider
            generated_image = free_provider.generate_image(
                prompt=prompt,
                size=parsed_params.get('size', '1024x1024'),
                style=parsed_params.get('style', 'photorealistic')
            )
            # Use the generated URL instead of the provided URL
            url = generated_image['url']
        except Exception as e:
            # Fall back to the provided URL if generation fails
            pass
    
    updated_material = await material_db.add_generated_image(
        material_id,
        url,
        prompt,
        ai_provider,
        parsed_params
    )
    if not updated_material:
        raise HTTPException(status_code=404, detail="Material not found")
    # Convert ObjectId to string for JSON serialization
    return serialize_material(updated_material)

@router.post("/{material_id}/select-image")
async def select_image(
    material_id: str,
    image_url: str,
    current_user: Annotated[dict, Depends(get_current_active_user)],
    request: Request
) -> Any:
    mongodb = request.app.mongodb
    materials_collection = get_db_collection(mongodb, "materials")
    material_db = MaterialDB(materials_collection)
    current_material = await material_db.get(material_id)
    if not current_material:
        raise HTTPException(status_code=404, detail="Material not found")
    if current_material["company_id"] != current_user["company_id"]:
        raise HTTPException(status_code=403, detail="Not enough permissions")
    
    updated_material = await material_db.select_image(material_id, image_url)
    if not updated_material:
        raise HTTPException(status_code=404, detail="Material not found")
    # Convert ObjectId to string for JSON serialization
    return serialize_material(updated_material)

@router.post("/{material_id}/feedback")
async def add_feedback(
    material_id: str,
    comment: str,
    current_user: Annotated[dict, Depends(get_current_active_user)],
    request: Request
) -> Any:
    mongodb = request.app.mongodb
    materials_collection = get_db_collection(mongodb, "materials")
    material_db = MaterialDB(materials_collection)
    current_material = await material_db.get(material_id)
    if not current_material:
        raise HTTPException(status_code=404, detail="Material not found")
    if current_material["company_id"] != current_user["company_id"]:
        raise HTTPException(status_code=403, detail="Not enough permissions")
    
    updated_material = await material_db.add_feedback(
        material_id,
        str(current_user["_id"]),
        comment
    )
    if not updated_material:
        raise HTTPException(status_code=404, detail="Material not found")
    # Convert ObjectId to string for JSON serialization
    return serialize_material(updated_material)

@router.post("/{material_id}/stage")
async def update_stage(
    material_id: str,
    stage: MaterialStage,
    current_user: Annotated[dict, Depends(get_current_active_user)],
    request: Request,
    status: MaterialStatus = MaterialStatus.IN_PROGRESS
) -> Any:
    mongodb = request.app.mongodb
    materials_collection = get_db_collection(mongodb, "materials")
    material_db = MaterialDB(materials_collection)
    current_material = await material_db.get(material_id)
    if not current_material:
        raise HTTPException(status_code=404, detail="Material not found")
    if current_material["company_id"] != current_user["company_id"]:
        raise HTTPException(status_code=403, detail="Not enough permissions")
    
    updated_material = await material_db.update_stage(material_id, stage, status)
    if not updated_material:
        raise HTTPException(status_code=404, detail="Material not found")
    # Convert ObjectId to string for JSON serialization
    return serialize_material(updated_material)

