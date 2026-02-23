"""
Material service — all business logic for the material lifecycle.

Layer contract (ARCH-LAYER-001):
  Route → material_service (this file) → MaterialDB → MongoDB

Serialisation helpers live here (ARCH-LAYER-002).
Stage transitions go through transition_stage() (ARCH-MAT-002).
Finalization guard is enforced in select_image() (ARCH-MAT-004).
"""
import logging
from typing import Any, List, Optional

from fastapi import HTTPException

from app.core.db_utils import get_db_collection
from app.db.material import MaterialDB
from app.models.material import (
    MaterialCreate,
    MaterialStage,
    MaterialStatus,
)

logger = logging.getLogger(__name__)


# ---------------------------------------------------------------------------
# Serialisation helpers (ARCH-LAYER-002 — moved from route file)
# ---------------------------------------------------------------------------

def serialize_material(material: dict) -> dict:
    """Convert MongoDB _id to string 'id' for JSON serialisation."""
    if material and "_id" in material:
        material["id"] = str(material["_id"])
        del material["_id"]
    return material


def serialize_materials(materials: List[dict]) -> List[dict]:
    """Serialise a list of material dicts."""
    return [serialize_material(m.copy()) for m in materials]


# ---------------------------------------------------------------------------
# Internal helper — single construction point for MaterialDB
# ---------------------------------------------------------------------------

def _make_db(db: Any) -> MaterialDB:
    """Construct MaterialDB from the Motor client provided by the route."""
    return MaterialDB(get_db_collection(db, "materials"))


# ---------------------------------------------------------------------------
# Public service API
# ---------------------------------------------------------------------------

async def create(
    db: Any,
    material: MaterialCreate,
    user_id: str,
    company_id: str,
) -> dict:
    """Create a new material and return the serialised document."""
    material_db = _make_db(db)
    created = await material_db.create_material(material, user_id, company_id)
    return serialize_material(created)


async def get(
    db: Any,
    material_id: str,
    company_id: str,
) -> dict:
    """Fetch a single material, enforcing company ownership."""
    material_db = _make_db(db)
    material = await material_db.get(material_id)
    if not material:
        raise HTTPException(status_code=404, detail="Material not found")
    if material["company_id"] != company_id:
        raise HTTPException(status_code=403, detail="Not enough permissions")
    return serialize_material(material)


async def list_materials(
    db: Any,
    company_id: str,
    stage: Optional[MaterialStage] = None,
    status: Optional[MaterialStatus] = None,
    skip: int = 0,
    limit: int = 100,
) -> List[dict]:
    """List materials for a company with optional stage/status filtering."""
    material_db = _make_db(db)
    materials = await material_db.get_company_materials(
        company_id, stage=stage, status=status, skip=skip, limit=limit
    )
    return serialize_materials(materials)


async def update(
    db: Any,
    material_id: str,
    company_id: str,
    update_data: dict,
) -> dict:
    """Apply a partial update dict to a material."""
    material_db = _make_db(db)
    current = await material_db.get(material_id)
    if not current:
        raise HTTPException(status_code=404, detail="Material not found")
    if current["company_id"] != company_id:
        raise HTTPException(status_code=403, detail="Not enough permissions")
    updated = await material_db.update(material_id, update_data)
    if not updated:
        raise HTTPException(status_code=404, detail="Material not found")
    return serialize_material(updated)


async def delete(
    db: Any,
    material_id: str,
    company_id: str,
) -> dict:
    """Delete a material and return a confirmation payload."""
    material_db = _make_db(db)
    current = await material_db.get(material_id)
    if not current:
        raise HTTPException(status_code=404, detail="Material not found")
    if current["company_id"] != company_id:
        raise HTTPException(status_code=403, detail="Not enough permissions")
    deleted = await material_db.delete(material_id)
    if not deleted:
        raise HTTPException(status_code=404, detail="Material not found")
    return {"success": True, "message": "Material deleted successfully", "id": material_id}


async def add_generated_image(
    db: Any,
    material_id: str,
    company_id: str,
    url: str,
    prompt: str,
    ai_provider: str,
    generation_params: dict,
) -> dict:
    """Append a generated image record to a material."""
    material_db = _make_db(db)
    current = await material_db.get(material_id)
    if not current:
        raise HTTPException(status_code=404, detail="Material not found")
    if current["company_id"] != company_id:
        raise HTTPException(status_code=403, detail="Not enough permissions")
    updated = await material_db.add_generated_image(
        material_id, url, prompt, ai_provider, generation_params
    )
    if not updated:
        raise HTTPException(status_code=404, detail="Material not found")
    return serialize_material(updated)


async def select_image(
    db: Any,
    material_id: str,
    company_id: str,
    image_url: str,
) -> dict:
    """
    Mark an image as selected and transition to finalization stage.

    ARCH-MAT-004 — Finalization Guard:
    A material with no generated images MUST NOT reach finalization.
    Raises HTTP 422 if generated_images is empty.
    """
    material_db = _make_db(db)
    current = await material_db.get(material_id)
    if not current:
        raise HTTPException(status_code=404, detail="Material not found")
    if current["company_id"] != company_id:
        raise HTTPException(status_code=403, detail="Not enough permissions")

    # ARCH-MAT-004: finalization guard
    if not current.get("generated_images"):
        logger.warning(
            "select_image: finalization guard triggered for material_id=%s", material_id
        )
        raise HTTPException(
            status_code=422,
            detail={
                "error_type": "finalization_guard",
                "user_message": "errors.material.no_generated_images",
                "http_status": 422,
            },
        )

    updated = await material_db.select_image(material_id, image_url)
    if not updated:
        raise HTTPException(status_code=404, detail="Material not found")
    return serialize_material(updated)


async def add_feedback(
    db: Any,
    material_id: str,
    company_id: str,
    user_id: str,
    comment: str,
) -> dict:
    """Append user feedback to a material."""
    material_db = _make_db(db)
    current = await material_db.get(material_id)
    if not current:
        raise HTTPException(status_code=404, detail="Material not found")
    if current["company_id"] != company_id:
        raise HTTPException(status_code=403, detail="Not enough permissions")
    updated = await material_db.add_feedback(material_id, user_id, comment)
    if not updated:
        raise HTTPException(status_code=404, detail="Material not found")
    return serialize_material(updated)


async def transition_stage(
    db: Any,
    material_id: str,
    company_id: str,
    stage: MaterialStage,
    status: MaterialStatus = MaterialStatus.IN_PROGRESS,
) -> dict:
    """
    Transition a material to a new stage (ARCH-MAT-002).

    Stage transitions MUST be performed exclusively in this service;
    route handlers MUST NOT write stage or status fields directly.
    """
    material_db = _make_db(db)
    current = await material_db.get(material_id)
    if not current:
        raise HTTPException(status_code=404, detail="Material not found")
    if current["company_id"] != company_id:
        raise HTTPException(status_code=403, detail="Not enough permissions")
    updated = await material_db.update_stage(material_id, stage, status)
    if not updated:
        raise HTTPException(status_code=404, detail="Material not found")
    return serialize_material(updated)
