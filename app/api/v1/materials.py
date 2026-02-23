from typing import Any, Annotated, Optional
from fastapi import APIRouter, Depends, Request, Query
from pydantic import BaseModel

from app.api.v1.deps import get_current_active_user
from app.models.material import (
    MaterialCreate,
    MaterialUpdate,
    MaterialStage,
    MaterialStatus,
)
import app.services.material_service as material_service

router = APIRouter()


class GeneratedImageInput(BaseModel):
    """Request body for POST /{material_id}/images (replaces raw Query params)."""
    url: str
    prompt: str
    ai_provider: str
    generation_params: dict = {}


@router.post("")
async def create_material(
    material: MaterialCreate,
    current_user: Annotated[dict, Depends(get_current_active_user)],
    request: Request,
) -> Any:
    db = request.app.mongodb
    return await material_service.create(
        db, material, str(current_user["_id"]), current_user["company_id"]
    )


@router.get("")
async def list_materials(
    current_user: Annotated[dict, Depends(get_current_active_user)],
    request: Request,
    stage: Optional[MaterialStage] = None,
    status: Optional[MaterialStatus] = None,
    skip: int = 0,
    limit: int = 100,
) -> Any:
    db = request.app.mongodb
    return await material_service.list_materials(
        db,
        current_user["company_id"],
        stage=stage,
        status=status,
        skip=skip,
        limit=limit,
    )


@router.get("/{material_id}")
async def get_material(
    material_id: str,
    current_user: Annotated[dict, Depends(get_current_active_user)],
    request: Request,
) -> Any:
    db = request.app.mongodb
    return await material_service.get(db, material_id, current_user["company_id"])


@router.put("/{material_id}")
async def update_material(
    material_id: str,
    material: MaterialUpdate,
    current_user: Annotated[dict, Depends(get_current_active_user)],
    request: Request,
) -> Any:
    db = request.app.mongodb
    update_data = material.model_dump(exclude_none=True)
    return await material_service.update(
        db, material_id, current_user["company_id"], update_data
    )


@router.post("/{material_id}/images")
async def add_generated_image(
    material_id: str,
    body: GeneratedImageInput,
    current_user: Annotated[dict, Depends(get_current_active_user)],
    request: Request,
) -> Any:
    db = request.app.mongodb
    return await material_service.add_generated_image(
        db,
        material_id,
        current_user["company_id"],
        body.url,
        body.prompt,
        body.ai_provider,
        body.generation_params,
    )


@router.post("/{material_id}/select-image")
async def select_image(
    material_id: str,
    image_url: Annotated[str, Query()],
    current_user: Annotated[dict, Depends(get_current_active_user)],
    request: Request,
) -> Any:
    db = request.app.mongodb
    return await material_service.select_image(
        db, material_id, current_user["company_id"], image_url
    )


@router.post("/{material_id}/feedback")
async def add_feedback(
    material_id: str,
    comment: Annotated[str, Query()],
    current_user: Annotated[dict, Depends(get_current_active_user)],
    request: Request,
) -> Any:
    db = request.app.mongodb
    return await material_service.add_feedback(
        db, material_id, current_user["company_id"], str(current_user["_id"]), comment
    )


@router.post("/{material_id}/stage")
async def update_stage(
    material_id: str,
    stage: MaterialStage,
    current_user: Annotated[dict, Depends(get_current_active_user)],
    request: Request,
    status: MaterialStatus = MaterialStatus.IN_PROGRESS,
) -> Any:
    db = request.app.mongodb
    return await material_service.transition_stage(
        db, material_id, current_user["company_id"], stage, status
    )


@router.delete("/{material_id}")
async def delete_material(
    material_id: str,
    current_user: Annotated[dict, Depends(get_current_active_user)],
    request: Request,
) -> Any:
    db = request.app.mongodb
    return await material_service.delete(db, material_id, current_user["company_id"])
