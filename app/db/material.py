import logging
from typing import List, Optional
from datetime import datetime

from app.db.base import BaseDB
from app.models.material import MaterialCreate, MaterialStage, MaterialStatus

logger = logging.getLogger(__name__)


class MaterialDB(BaseDB):
    async def create_material(
        self, material: MaterialCreate, user_id: str, company_id: str
    ) -> dict:
        material_data = material.model_dump()
        material_data.update({
            "company_id": company_id,
            "created_by": user_id,
            "generated_images": [],
            "feedback": [],
            "version_history": [],
        })
        return await self.create(material_data)

    async def get_company_materials(
        self,
        company_id: str,
        stage: Optional[MaterialStage] = None,
        status: Optional[MaterialStatus] = None,
        skip: int = 0,
        limit: int = 100,
    ) -> List[dict]:
        """Get materials for a company with optional stage/status filtering."""
        query: dict = {"company_id": company_id}
        if stage:
            query["stage"] = stage
        if status:
            query["status"] = status

        logger.debug("get_company_materials: company_id=%s query=%s", company_id, query)
        cursor = self.collection.find(query).skip(skip).limit(limit)
        return await cursor.to_list(length=limit)

    async def add_generated_image(
        self,
        material_id: str,
        url: str,
        prompt: str,
        ai_provider: str,
        generation_params: dict,
    ) -> Optional[dict]:
        image_data = {
            "url": url,
            "prompt": prompt,
            "ai_provider": ai_provider,
            "generation_params": generation_params,
            "created_at": datetime.utcnow(),
        }
        result = await self.collection.update_one(
            {"_id": material_id},
            {"$push": {"generated_images": image_data}},
        )
        return await self.get(material_id) if result.modified_count > 0 else None

    async def select_image(self, material_id: str, image_url: str) -> Optional[dict]:
        return await self.update(material_id, {"selected_image": image_url})

    async def add_feedback(
        self,
        material_id: str,
        user_id: str,
        comment: str,
    ) -> Optional[dict]:
        feedback_data = {
            "user_id": user_id,
            "comment": comment,
            "created_at": datetime.utcnow(),
        }
        result = await self.collection.update_one(
            {"_id": material_id},
            {"$push": {"feedback": feedback_data}},
        )
        return await self.get(material_id) if result.modified_count > 0 else None

    async def update_stage(
        self,
        material_id: str,
        stage: MaterialStage,
        status: MaterialStatus = MaterialStatus.IN_PROGRESS,
    ) -> Optional[dict]:
        return await self.update(material_id, {"stage": stage, "status": status})
