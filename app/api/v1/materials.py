from typing import Any, List, Optional, Annotated
from datetime import datetime
from fastapi import APIRouter, Depends, HTTPException, File, UploadFile, Request
from motor.motor_asyncio import AsyncIOMotorClient

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
    # Return directly without validation through response_model
    return created_material

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
    
    # Return directly without validation through response_model
    return materials

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
    # Return directly without validation through response_model
    return material

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
    # Return directly without validation through response_model
    return updated_material

@router.post("/{material_id}/images")
async def add_generated_image(
    material_id: str,
    url: str,
    prompt: str,
    ai_provider: str,
    generation_params: dict,
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
    
    updated_material = await material_db.add_generated_image(
        material_id,
        url,
        prompt,
        ai_provider,
        generation_params
    )
    if not updated_material:
        raise HTTPException(status_code=404, detail="Material not found")
    return updated_material

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
    return updated_material

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
    return updated_material

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
    return updated_material
